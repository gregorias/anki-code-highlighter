import unittest

from codehighlighter.migratev2 import hljs_to_pygments_lang


class TestHljsToPygmentsLang(unittest.TestCase):
    def test_hljs_to_pygments_lang_for_abnf(self):
        self.assertEqual(hljs_to_pygments_lang("abnf"), "ABNF")

    def test_hljs_to_pygments_lang_for_actionscript(self):
        self.assertEqual(hljs_to_pygments_lang("actionscript"), "ActionScript")

    def test_hljs_to_pygments_lang_for_ada(self):
        self.assertEqual(hljs_to_pygments_lang("ada"), "Ada")

    def test_hljs_to_pygments_lang_for_apache(self):
        self.assertEqual(hljs_to_pygments_lang("apache"), "ApacheConf")

    def test_hljs_to_pygments_lang_for_applescript(self):
        self.assertEqual(hljs_to_pygments_lang("applescript"), "AppleScript")

    def test_hljs_to_pygments_lang_for_arduino(self):
        self.assertEqual(hljs_to_pygments_lang("arduino"), "Arduino")

    def test_hljs_to_pygments_lang_for_armasm(self):
        self.assertEqual(hljs_to_pygments_lang("armasm"), "ARM")

    def test_hljs_to_pygments_lang_for_asciidoc(self):
        self.assertEqual(hljs_to_pygments_lang("asciidoc"), None)

    def test_hljs_to_pygments_lang_for_aspectj(self):
        self.assertEqual(hljs_to_pygments_lang("aspectj"), "AspectJ")

    def test_hljs_to_pygments_lang_for_autohotkey(self):
        self.assertEqual(hljs_to_pygments_lang("autohotkey"), "autohotkey")

    def test_hljs_to_pygments_lang_for_autoit(self):
        self.assertEqual(hljs_to_pygments_lang("autoit"), "AutoIt")

    def test_hljs_to_pygments_lang_for_avrasm(self):
        self.assertEqual(hljs_to_pygments_lang("avrasm"), "ARM")

    def test_hljs_to_pygments_lang_for_awk(self):
        self.assertEqual(hljs_to_pygments_lang("awk"), "Awk")

    def test_hljs_to_pygments_lang_for_bash(self):
        self.assertEqual(hljs_to_pygments_lang("bash"), "Bash")

    def test_hljs_to_pygments_lang_for_basic(self):
        self.assertEqual(hljs_to_pygments_lang("basic"), "QBasic")

    def test_hljs_to_pygments_lang_for_bnf(self):
        self.assertEqual(hljs_to_pygments_lang("bnf"), "BNF")

    def test_hljs_to_pygments_lang_for_brainfuck(self):
        self.assertEqual(hljs_to_pygments_lang("brainfuck"), "Brainfuck")

    def test_hljs_to_pygments_lang_for_c(self):
        self.assertEqual(hljs_to_pygments_lang("c"), "C")

    def test_hljs_to_pygments_lang_for_cal(self):
        self.assertEqual(hljs_to_pygments_lang("cal"), None)

    def test_hljs_to_pygments_lang_for_capnproto(self):
        self.assertEqual(hljs_to_pygments_lang("capnproto"), None)

    def test_hljs_to_pygments_lang_for_ceylon(self):
        self.assertEqual(hljs_to_pygments_lang("ceylon"), "Ceylon")

    def test_hljs_to_pygments_lang_for_clean(self):
        self.assertEqual(hljs_to_pygments_lang("clean"), "Clean")

    def test_hljs_to_pygments_lang_for_clojure(self):
        self.assertEqual(hljs_to_pygments_lang("clojure"), "Clojure")

    def test_hljs_to_pygments_lang_for_clojure_repl(self):
        self.assertEqual(hljs_to_pygments_lang("clojure-repl"), None)

    def test_hljs_to_pygments_lang_for_cmake(self):
        self.assertEqual(hljs_to_pygments_lang("cmake"), "CMake")

    def test_hljs_to_pygments_lang_for_coffeescript(self):
        self.assertEqual(hljs_to_pygments_lang("coffeescript"), "CoffeeScript")

    def test_hljs_to_pygments_lang_for_coq(self):
        self.assertEqual(hljs_to_pygments_lang("coq"), "Coq")

    def test_hljs_to_pygments_lang_for_cos(self):
        self.assertEqual(hljs_to_pygments_lang("cos"), None)

    def test_hljs_to_pygments_lang_for_cpp(self):
        self.assertEqual(hljs_to_pygments_lang("cpp"), "C++")

    def test_hljs_to_pygments_lang_for_crmsh(self):
        self.assertEqual(hljs_to_pygments_lang("crmsh"), "Crmsh")

    def test_hljs_to_pygments_lang_for_crystal(self):
        self.assertEqual(hljs_to_pygments_lang("crystal"), "Crystal")

    def test_hljs_to_pygments_lang_for_csharp(self):
        self.assertEqual(hljs_to_pygments_lang("csharp"), "C#")

    def test_hljs_to_pygments_lang_for_csp(self):
        self.assertEqual(hljs_to_pygments_lang("csp"), None)

    def test_hljs_to_pygments_lang_for_css(self):
        self.assertEqual(hljs_to_pygments_lang("css"), "CSS")

    def test_hljs_to_pygments_lang_for_d(self):
        self.assertEqual(hljs_to_pygments_lang("d"), "D")

    def test_hljs_to_pygments_lang_for_dart(self):
        self.assertEqual(hljs_to_pygments_lang("dart"), "Dart")

    def test_hljs_to_pygments_lang_for_delphi(self):
        self.assertEqual(hljs_to_pygments_lang("delphi"), "Delphi")

    def test_hljs_to_pygments_lang_for_diff(self):
        self.assertEqual(hljs_to_pygments_lang("diff"), "Diff")

    def test_hljs_to_pygments_lang_for_django(self):
        self.assertEqual(hljs_to_pygments_lang("django"), "Django/Jinja")

    def test_hljs_to_pygments_lang_for_dns(self):
        self.assertEqual(hljs_to_pygments_lang("dns"), None)

    def test_hljs_to_pygments_lang_for_dockerfile(self):
        self.assertEqual(hljs_to_pygments_lang("dockerfile"), "Docker")

    def test_hljs_to_pygments_lang_for_dos(self):
        self.assertEqual(hljs_to_pygments_lang("dos"), None)

    def test_hljs_to_pygments_lang_for_dsconfig(self):
        self.assertEqual(hljs_to_pygments_lang("dsconfig"), None)

    def test_hljs_to_pygments_lang_for_dts(self):
        self.assertEqual(hljs_to_pygments_lang("dts"), "Devicetree")

    def test_hljs_to_pygments_lang_for_dust(self):
        self.assertEqual(hljs_to_pygments_lang("dust"), None)

    def test_hljs_to_pygments_lang_for_ebnf(self):
        self.assertEqual(hljs_to_pygments_lang("ebnf"), "EBNF")

    def test_hljs_to_pygments_lang_for_elixir(self):
        self.assertEqual(hljs_to_pygments_lang("elixir"), "Elixir")

    def test_hljs_to_pygments_lang_for_elm(self):
        self.assertEqual(hljs_to_pygments_lang("elm"), "Elm")

    def test_hljs_to_pygments_lang_for_erb(self):
        self.assertEqual(hljs_to_pygments_lang("erb"), "ERB")

    def test_hljs_to_pygments_lang_for_erlang(self):
        self.assertEqual(hljs_to_pygments_lang("erlang"), "Erlang")

    def test_hljs_to_pygments_lang_for_erlang_repl(self):
        self.assertEqual(hljs_to_pygments_lang("erlang-repl"), None)

    def test_hljs_to_pygments_lang_for_excel(self):
        self.assertEqual(hljs_to_pygments_lang("excel"), None)

    def test_hljs_to_pygments_lang_for_fix(self):
        self.assertEqual(hljs_to_pygments_lang("fix"), None)

    def test_hljs_to_pygments_lang_for_flix(self):
        self.assertEqual(hljs_to_pygments_lang("flix"), None)

    def test_hljs_to_pygments_lang_for_fortran(self):
        self.assertEqual(hljs_to_pygments_lang("fortran"), "Fortran")

    def test_hljs_to_pygments_lang_for_fsharp(self):
        self.assertEqual(hljs_to_pygments_lang("fsharp"), "F#")

    def test_hljs_to_pygments_lang_for_gams(self):
        self.assertEqual(hljs_to_pygments_lang("gams"), None)

    def test_hljs_to_pygments_lang_for_gauss(self):
        self.assertEqual(hljs_to_pygments_lang("gauss"), None)

    def test_hljs_to_pygments_lang_for_gcode(self):
        self.assertEqual(hljs_to_pygments_lang("gcode"), "g-code")

    def test_hljs_to_pygments_lang_for_gherkin(self):
        self.assertEqual(hljs_to_pygments_lang("gherkin"), "Gherkin")

    def test_hljs_to_pygments_lang_for_glsl(self):
        self.assertEqual(hljs_to_pygments_lang("glsl"), "GLSL")

    def test_hljs_to_pygments_lang_for_gml(self):
        self.assertEqual(hljs_to_pygments_lang("gml"), None)

    def test_hljs_to_pygments_lang_for_go(self):
        self.assertEqual(hljs_to_pygments_lang("go"), "Go")

    def test_hljs_to_pygments_lang_for_golo(self):
        self.assertEqual(hljs_to_pygments_lang("golo"), "Golo")

    def test_hljs_to_pygments_lang_for_gradle(self):
        self.assertEqual(hljs_to_pygments_lang("gradle"), "Groovy")

    def test_hljs_to_pygments_lang_for_graphql(self):
        self.assertEqual(hljs_to_pygments_lang("graphql"), "GraphQL")

    def test_hljs_to_pygments_lang_for_groovy(self):
        self.assertEqual(hljs_to_pygments_lang("groovy"), "Groovy")

    def test_hljs_to_pygments_lang_for_haml(self):
        self.assertEqual(hljs_to_pygments_lang("haml"), "Haml")

    def test_hljs_to_pygments_lang_for_handlebars(self):
        self.assertEqual(hljs_to_pygments_lang("handlebars"), "Handlebars")

    def test_hljs_to_pygments_lang_for_haskell(self):
        self.assertEqual(hljs_to_pygments_lang("haskell"), "Haskell")

    def test_hljs_to_pygments_lang_for_haxe(self):
        self.assertEqual(hljs_to_pygments_lang("haxe"), "Haxe")

    def test_hljs_to_pygments_lang_for_hsp(self):
        self.assertEqual(hljs_to_pygments_lang("hsp"), None)

    def test_hljs_to_pygments_lang_for_http(self):
        self.assertEqual(hljs_to_pygments_lang("http"), "HTTP")

    def test_hljs_to_pygments_lang_for_hy(self):
        self.assertEqual(hljs_to_pygments_lang("hy"), "Hy")

    def test_hljs_to_pygments_lang_for_inform7(self):
        self.assertEqual(hljs_to_pygments_lang("inform7"), "Inform 7")

    def test_hljs_to_pygments_lang_for_ini(self):
        self.assertEqual(hljs_to_pygments_lang("ini"), "INI")

    def test_hljs_to_pygments_lang_for_irpf90(self):
        self.assertEqual(hljs_to_pygments_lang("irpf90"), None)

    def test_hljs_to_pygments_lang_for_isbl(self):
        self.assertEqual(hljs_to_pygments_lang("isbl"), None)

    def test_hljs_to_pygments_lang_for_java(self):
        self.assertEqual(hljs_to_pygments_lang("java"), "Java")

    def test_hljs_to_pygments_lang_for_javascript(self):
        self.assertEqual(hljs_to_pygments_lang("javascript"), "JavaScript")

    def test_hljs_to_pygments_lang_for_jboss_cli(self):
        self.assertEqual(hljs_to_pygments_lang("jboss-cli"), None)

    def test_hljs_to_pygments_lang_for_json(self):
        self.assertEqual(hljs_to_pygments_lang("json"), "JSON")

    def test_hljs_to_pygments_lang_for_julia(self):
        self.assertEqual(hljs_to_pygments_lang("julia"), "Julia")

    def test_hljs_to_pygments_lang_for_julia_repl(self):
        self.assertEqual(hljs_to_pygments_lang("julia-repl"), "Julia console")

    def test_hljs_to_pygments_lang_for_kotlin(self):
        self.assertEqual(hljs_to_pygments_lang("kotlin"), "Kotlin")

    def test_hljs_to_pygments_lang_for_lasso(self):
        self.assertEqual(hljs_to_pygments_lang("lasso"), "Lasso")

    def test_hljs_to_pygments_lang_for_latex(self):
        self.assertEqual(hljs_to_pygments_lang("latex"), "TeX")

    def test_hljs_to_pygments_lang_for_ldif(self):
        self.assertEqual(hljs_to_pygments_lang("ldif"), "LDIF")

    def test_hljs_to_pygments_lang_for_leaf(self):
        self.assertEqual(hljs_to_pygments_lang("leaf"), None)

    def test_hljs_to_pygments_lang_for_less(self):
        self.assertEqual(hljs_to_pygments_lang("less"), "LessCss")

    def test_hljs_to_pygments_lang_for_lisp(self):
        self.assertEqual(hljs_to_pygments_lang("lisp"), "Common Lisp")

    def test_hljs_to_pygments_lang_for_livecodeserver(self):
        self.assertEqual(hljs_to_pygments_lang("livecodeserver"), None)

    def test_hljs_to_pygments_lang_for_livescript(self):
        self.assertEqual(hljs_to_pygments_lang("livescript"), "LiveScript")

    def test_hljs_to_pygments_lang_for_llvm(self):
        self.assertEqual(hljs_to_pygments_lang("llvm"), "LLVM")

    def test_hljs_to_pygments_lang_for_lsl(self):
        self.assertEqual(hljs_to_pygments_lang("lsl"), "LSL")

    def test_hljs_to_pygments_lang_for_lua(self):
        self.assertEqual(hljs_to_pygments_lang("lua"), "Lua")

    def test_hljs_to_pygments_lang_for_makefile(self):
        self.assertEqual(hljs_to_pygments_lang("makefile"), "Makefile")

    def test_hljs_to_pygments_lang_for_markdown(self):
        self.assertEqual(hljs_to_pygments_lang("markdown"), "Markdown")

    def test_hljs_to_pygments_lang_for_mathematica(self):
        self.assertEqual(hljs_to_pygments_lang("mathematica"), "Mathematica")

    def test_hljs_to_pygments_lang_for_matlab(self):
        self.assertEqual(hljs_to_pygments_lang("matlab"), "Matlab")

    def test_hljs_to_pygments_lang_for_maxima(self):
        self.assertEqual(hljs_to_pygments_lang("maxima"), "Maxima")

    def test_hljs_to_pygments_lang_for_mel(self):
        self.assertEqual(hljs_to_pygments_lang("mel"), None)

    def test_hljs_to_pygments_lang_for_mercury(self):
        self.assertEqual(hljs_to_pygments_lang("mercury"), None)

    def test_hljs_to_pygments_lang_for_mipsasm(self):
        self.assertEqual(hljs_to_pygments_lang("mipsasm"), None)

    def test_hljs_to_pygments_lang_for_mizar(self):
        self.assertEqual(hljs_to_pygments_lang("mizar"), None)

    def test_hljs_to_pygments_lang_for_mojolicious(self):
        self.assertEqual(hljs_to_pygments_lang("mojolicious"), None)

    def test_hljs_to_pygments_lang_for_monkey(self):
        self.assertEqual(hljs_to_pygments_lang("monkey"), "Monkey")

    def test_hljs_to_pygments_lang_for_moonscript(self):
        self.assertEqual(hljs_to_pygments_lang("moonscript"), "MoonScript")

    def test_hljs_to_pygments_lang_for_n1ql(self):
        self.assertEqual(hljs_to_pygments_lang("n1ql"), None)

    def test_hljs_to_pygments_lang_for_nestedtext(self):
        self.assertEqual(hljs_to_pygments_lang("nestedtext"), "NestedText")

    def test_hljs_to_pygments_lang_for_nginx(self):
        self.assertEqual(hljs_to_pygments_lang("nginx"), "Nginx configuration file")

    def test_hljs_to_pygments_lang_for_nim(self):
        self.assertEqual(hljs_to_pygments_lang("nim"), "Nimrod")

    def test_hljs_to_pygments_lang_for_nix(self):
        self.assertEqual(hljs_to_pygments_lang("nix"), "Nix")

    def test_hljs_to_pygments_lang_for_node_repl(self):
        self.assertEqual(hljs_to_pygments_lang("node-repl"), None)

    def test_hljs_to_pygments_lang_for_nsis(self):
        self.assertEqual(hljs_to_pygments_lang("nsis"), "NSIS")

    def test_hljs_to_pygments_lang_for_objectivec(self):
        self.assertEqual(hljs_to_pygments_lang("objectivec"), "Objective-C")

    def test_hljs_to_pygments_lang_for_ocaml(self):
        self.assertEqual(hljs_to_pygments_lang("ocaml"), "OCaml")

    def test_hljs_to_pygments_lang_for_openscad(self):
        self.assertEqual(hljs_to_pygments_lang("openscad"), "OpenSCAD")

    def test_hljs_to_pygments_lang_for_oxygene(self):
        self.assertEqual(hljs_to_pygments_lang("oxygene"), None)

    def test_hljs_to_pygments_lang_for_parser3(self):
        self.assertEqual(hljs_to_pygments_lang("parser3"), None)

    def test_hljs_to_pygments_lang_for_perl(self):
        self.assertEqual(hljs_to_pygments_lang("perl"), "Perl")

    def test_hljs_to_pygments_lang_for_pf(self):
        self.assertEqual(hljs_to_pygments_lang("pf"), None)

    def test_hljs_to_pygments_lang_for_pgsql(self):
        self.assertEqual(hljs_to_pygments_lang("pgsql"), None)

    def test_hljs_to_pygments_lang_for_php(self):
        self.assertEqual(hljs_to_pygments_lang("php"), "PHP")

    def test_hljs_to_pygments_lang_for_php_template(self):
        self.assertEqual(hljs_to_pygments_lang("php-template"), None)

    def test_hljs_to_pygments_lang_for_plaintext(self):
        self.assertEqual(hljs_to_pygments_lang("plaintext"), "plaintext")

    def test_hljs_to_pygments_lang_for_pony(self):
        self.assertEqual(hljs_to_pygments_lang("pony"), "Pony")

    def test_hljs_to_pygments_lang_for_powershell(self):
        self.assertEqual(hljs_to_pygments_lang("powershell"), "PowerShell")

    def test_hljs_to_pygments_lang_for_processing(self):
        self.assertEqual(hljs_to_pygments_lang("processing"), None)

    def test_hljs_to_pygments_lang_for_profile(self):
        self.assertEqual(hljs_to_pygments_lang("profile"), None)

    def test_hljs_to_pygments_lang_for_prolog(self):
        self.assertEqual(hljs_to_pygments_lang("prolog"), "Prolog")

    def test_hljs_to_pygments_lang_for_properties(self):
        self.assertEqual(hljs_to_pygments_lang("properties"), "Properties")

    def test_hljs_to_pygments_lang_for_protobuf(self):
        self.assertEqual(hljs_to_pygments_lang("protobuf"), "Protocol Buffer")

    def test_hljs_to_pygments_lang_for_puppet(self):
        self.assertEqual(hljs_to_pygments_lang("puppet"), "Puppet")

    def test_hljs_to_pygments_lang_for_purebasic(self):
        self.assertEqual(hljs_to_pygments_lang("purebasic"), None)

    def test_hljs_to_pygments_lang_for_python(self):
        self.assertEqual(hljs_to_pygments_lang("python"), "Python")

    def test_hljs_to_pygments_lang_for_python_repl(self):
        self.assertEqual(hljs_to_pygments_lang("python-repl"), None)

    def test_hljs_to_pygments_lang_for_q(self):
        self.assertEqual(hljs_to_pygments_lang("q"), "Q")

    def test_hljs_to_pygments_lang_for_qml(self):
        self.assertEqual(hljs_to_pygments_lang("qml"), "QML")

    def test_hljs_to_pygments_lang_for_r(self):
        self.assertEqual(hljs_to_pygments_lang("r"), "S")

    def test_hljs_to_pygments_lang_for_reasonml(self):
        self.assertEqual(hljs_to_pygments_lang("reasonml"), "ReasonML")

    def test_hljs_to_pygments_lang_for_rib(self):
        self.assertEqual(hljs_to_pygments_lang("rib"), None)

    def test_hljs_to_pygments_lang_for_riscvasm(self):
        # I added riscvasm as a language for Highlight.js.
        # Moving to ARM, because it should work just as well.
        self.assertEqual(hljs_to_pygments_lang("riscvasm"), "ARM")

    def test_hljs_to_pygments_lang_for_roboconf(self):
        self.assertEqual(hljs_to_pygments_lang("roboconf"), None)

    def test_hljs_to_pygments_lang_for_routeros(self):
        self.assertEqual(hljs_to_pygments_lang("routeros"), None)

    def test_hljs_to_pygments_lang_for_rsl(self):
        self.assertEqual(hljs_to_pygments_lang("rsl"), "RSL")

    def test_hljs_to_pygments_lang_for_ruby(self):
        self.assertEqual(hljs_to_pygments_lang("ruby"), "Ruby")

    def test_hljs_to_pygments_lang_for_ruleslanguage(self):
        self.assertEqual(hljs_to_pygments_lang("ruleslanguage"), None)

    def test_hljs_to_pygments_lang_for_rust(self):
        self.assertEqual(hljs_to_pygments_lang("rust"), "Rust")

    def test_hljs_to_pygments_lang_for_sas(self):
        self.assertEqual(hljs_to_pygments_lang("sas"), "SAS")

    def test_hljs_to_pygments_lang_for_scala(self):
        self.assertEqual(hljs_to_pygments_lang("scala"), "Scala")

    def test_hljs_to_pygments_lang_for_scheme(self):
        self.assertEqual(hljs_to_pygments_lang("scheme"), "Scheme")

    def test_hljs_to_pygments_lang_for_scilab(self):
        self.assertEqual(hljs_to_pygments_lang("scilab"), "Scilab")

    def test_hljs_to_pygments_lang_for_scss(self):
        self.assertEqual(hljs_to_pygments_lang("scss"), "SCSS")

    def test_hljs_to_pygments_lang_for_shell(self):
        self.assertEqual(hljs_to_pygments_lang("shell"), "Bash")

    def test_hljs_to_pygments_lang_for_smali(self):
        self.assertEqual(hljs_to_pygments_lang("smali"), "Smali")

    def test_hljs_to_pygments_lang_for_smalltalk(self):
        self.assertEqual(hljs_to_pygments_lang("smalltalk"), "Smalltalk")

    def test_hljs_to_pygments_lang_for_sml(self):
        self.assertEqual(hljs_to_pygments_lang("sml"), "Standard ML")

    def test_hljs_to_pygments_lang_for_sqf(self):
        self.assertEqual(hljs_to_pygments_lang("sqf"), None)

    def test_hljs_to_pygments_lang_for_sql(self):
        self.assertEqual(hljs_to_pygments_lang("sql"), "SQL")

    def test_hljs_to_pygments_lang_for_stan(self):
        self.assertEqual(hljs_to_pygments_lang("stan"), "Stan")

    def test_hljs_to_pygments_lang_for_stata(self):
        self.assertEqual(hljs_to_pygments_lang("stata"), "Stata")

    def test_hljs_to_pygments_lang_for_step21(self):
        self.assertEqual(hljs_to_pygments_lang("step21"), None)

    def test_hljs_to_pygments_lang_for_stylus(self):
        self.assertEqual(hljs_to_pygments_lang("stylus"), None)

    def test_hljs_to_pygments_lang_for_subunit(self):
        self.assertEqual(hljs_to_pygments_lang("subunit"), None)

    def test_hljs_to_pygments_lang_for_swift(self):
        self.assertEqual(hljs_to_pygments_lang("swift"), "Swift")

    def test_hljs_to_pygments_lang_for_taggerscript(self):
        self.assertEqual(hljs_to_pygments_lang("taggerscript"), None)

    def test_hljs_to_pygments_lang_for_tap(self):
        self.assertEqual(hljs_to_pygments_lang("tap"), "TAP")

    def test_hljs_to_pygments_lang_for_tcl(self):
        self.assertEqual(hljs_to_pygments_lang("tcl"), "Tcl")

    def test_hljs_to_pygments_lang_for_thrift(self):
        self.assertEqual(hljs_to_pygments_lang("thrift"), "Thrift")

    def test_hljs_to_pygments_lang_for_tp(self):
        self.assertEqual(hljs_to_pygments_lang("tp"), None)

    def test_hljs_to_pygments_lang_for_twig(self):
        self.assertEqual(hljs_to_pygments_lang("twig"), "Twig")

    def test_hljs_to_pygments_lang_for_typescript(self):
        self.assertEqual(hljs_to_pygments_lang("typescript"), "TypeScript")

    def test_hljs_to_pygments_lang_for_vala(self):
        self.assertEqual(hljs_to_pygments_lang("vala"), "Vala")

    def test_hljs_to_pygments_lang_for_vbnet(self):
        self.assertEqual(hljs_to_pygments_lang("vbnet"), "VB.net")

    def test_hljs_to_pygments_lang_for_vbscript(self):
        self.assertEqual(hljs_to_pygments_lang("vbscript"), "VBScript")

    def test_hljs_to_pygments_lang_for_vbscript_html(self):
        self.assertEqual(hljs_to_pygments_lang("vbscript-html"), None)

    def test_hljs_to_pygments_lang_for_verilog(self):
        self.assertEqual(hljs_to_pygments_lang("verilog"), "verilog")

    def test_hljs_to_pygments_lang_for_vhdl(self):
        self.assertEqual(hljs_to_pygments_lang("vhdl"), "vhdl")

    def test_hljs_to_pygments_lang_for_vim(self):
        self.assertEqual(hljs_to_pygments_lang("vim"), "VimL")

    def test_hljs_to_pygments_lang_for_wasm(self):
        self.assertEqual(hljs_to_pygments_lang("wasm"), "WebAssembly")

    def test_hljs_to_pygments_lang_for_wren(self):
        self.assertEqual(hljs_to_pygments_lang("wren"), "Wren")

    def test_hljs_to_pygments_lang_for_x86asm(self):
        self.assertEqual(hljs_to_pygments_lang("x86asm"), "NASM")

    def test_hljs_to_pygments_lang_for_xml(self):
        self.assertEqual(hljs_to_pygments_lang("xml"), "XML")

    def test_hljs_to_pygments_lang_for_xquery(self):
        self.assertEqual(hljs_to_pygments_lang("xquery"), "XQuery")

    def test_hljs_to_pygments_lang_for_yaml(self):
        self.assertEqual(hljs_to_pygments_lang("yaml"), "YAML")

    def test_hljs_to_pygments_lang_for_zephir(self):
        self.assertEqual(hljs_to_pygments_lang("zephir"), "Zephir")
