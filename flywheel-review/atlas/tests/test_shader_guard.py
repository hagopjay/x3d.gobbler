from __future__ import annotations

from pathlib import Path
import sys
import unittest
from xml.sax.saxutils import quoteattr

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import shader_guard as guard


def shader_url(mfstring: str) -> bytes:
    return f'<X3D><Scene><ShaderPart url={quoteattr(mfstring)}/></Scene></X3D>'.encode()


class ShaderGuardTests(unittest.TestCase):
    def test_raw_glsl_in_mfstring_is_rejected(self):
        result = guard.inspect_shader_xml(shader_url('"void main() { gl_Position = vec4(1.0); }"'))
        self.assertFalse(result["ok"])
        self.assertEqual(result["diagnostics"][0]["code"], "SHADER_RAW_SOURCE")

    def test_unquoted_raw_glsl_is_also_rejected(self):
        self.assertFalse(guard.inspect_shader_xml(shader_url('void main() { gl_Position = vec4(1.0); }'))["ok"])

    def test_raw_glsl_cdata_is_rejected(self):
        result = guard.inspect_shader_xml(b'<X3D><Scene><ShaderPart><![CDATA[#version 300 es\nvoid main() {}]]></ShaderPart></Scene></X3D>')
        self.assertFalse(result["ok"])
        self.assertEqual(result["diagnostics"][0]["channel"], "text")

    def test_shader_data_uri_in_mfstring_is_accepted(self):
        result = guard.inspect_shader_xml(shader_url('"data:x-shader/x-fragment,void main() { outputColor = vec4(1.0); }"'))
        self.assertTrue(result["ok"])
        self.assertEqual(result["references"][0]["kind"], "data-uri")

    def test_shader_data_uri_cdata_preserves_spaces_and_newlines(self):
        result = guard.inspect_shader_xml(b'<X3D><Scene><ShaderPart><![CDATA[data:x-shader/x-vertex,#version 300 es\nvoid main() {}]]></ShaderPart></Scene></X3D>')
        self.assertTrue(result["ok"])
        self.assertEqual(len(result["references"]), 1)
        self.assertEqual(result["references"][0]["kind"], "data-uri")

    def test_https_and_relative_fallback_urls_are_accepted(self):
        result = guard.inspect_shader_xml(shader_url('"https://example.org/shader.glsl" "../shaders/fallback.glsl"'))
        self.assertTrue(result["ok"])
        self.assertEqual([r["kind"] for r in result["references"]], ["external-url", "relative-or-other-url"])

    def test_explicit_url_with_code_in_query_is_still_a_url(self):
        result = guard.inspect_shader_xml(shader_url('"https://example.org/shader?source=void main(){}"'))
        self.assertTrue(result["ok"])

    def test_a_good_fallback_does_not_hide_raw_glsl(self):
        result = guard.inspect_shader_xml(shader_url('"https://example.org/shader.glsl" void main(){}'))
        self.assertFalse(result["ok"])

    def test_malformed_mfstring_fails_closed(self):
        result = guard.inspect_shader_xml(shader_url('"missing-end-quote.glsl'))
        self.assertFalse(result["ok"])
        self.assertEqual(result["diagnostics"][0]["code"], "SHADER_REFERENCE_PARSE_ERROR")

    def test_malformed_xml_has_separate_diagnostic(self):
        result = guard.inspect_shader_xml(b'<X3D><Scene>')
        self.assertFalse(result["ok"])
        self.assertEqual(result["diagnostics"][0]["code"], "XML_PARSE_ERROR")

    def test_namespaced_xml_is_examined(self):
        result = guard.inspect_shader_xml(b'<X3D xmlns="https://www.web3d.org/specifications/x3d-namespace"><ShaderPart><![CDATA[void main(){}]]></ShaderPart></X3D>')
        self.assertFalse(result["ok"])
        self.assertEqual(result["shaderParts"], 1)

    def test_executed_foldback_report_is_reproducible_and_scoped(self):
        first = guard.run_foldback()
        self.assertEqual(guard.canonical_bytes(first), guard.canonical_bytes(guard.run_foldback()))
        self.assertTrue(first["ok"])
        self.assertFalse(first["synthetic"])
        self.assertTrue(first["authoredFixtures"])
        self.assertEqual(len(first["results"]), 5)
        self.assertEqual(sum(not r["ok"] for r in first["results"]), 2)
        self.assertTrue(first["localTransfer"]["accepted"])
        self.assertEqual((first["localTransfer"]["origin"], first["localTransfer"]["consumer"]), ("gamedev", "music"))
        self.assertTrue(any("not a live" in limit for limit in first["limits"]))


if __name__ == "__main__":
    unittest.main()
