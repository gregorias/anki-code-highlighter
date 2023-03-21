import unittest

import bs4

from codehighlighter.ankieditorextra import extract_field_from_web_editor, transform_elements_with_id


class AnkiEditorExtraTestCase(unittest.TestCase):

    def test_find_id_elements_and_replace(self):
        field = "<div>Lorem Ipsum</div><div id='foobar123'>code</div>"

        def replace(html: str) -> bs4.Tag:
            soup = bs4.BeautifulSoup()
            code_tag = soup.new_tag('code')
            code_tag.append(html)
            soup.append(code_tag)
            return soup

        expected = "<div>Lorem Ipsum</div><code>code</code>"
        self.assertEqual(
            transform_elements_with_id(field, 'foobar123', replace), expected)

    def test_extract_field_from_web_editor_extracts_field_0(self):
        self.assertEqual(
            extract_field_from_web_editor(
                '<link id="rootStyle" rel="stylesheet" href="./_anki/css/editable.css"><style id="userBase"></style><anki-editable contenteditable="true" class="svelte-18uwveo" style="--editor-shrink-max-width:250px; --editor-shrink-max-height:125px;"><span id="2208">asdf</span></anki-editable>'
            ), '<span id="2208">asdf</span>')

    def test_extract_field_from_web_editor_extracts_field_1(self):
        self.assertEqual(
            extract_field_from_web_editor('''
                <link id="rootStyle" rel="stylesheet" href="./_anki/css/editable.css">
                <style id="userBase"></style>
                <anki-editable contenteditable="true" class="svelte-18uwveo" style="--editor-shrink-max-width:250px; --editor-shrink-max-height:125px;">
                    <span id="2208">asdf</span>
                    Lorem Ipsum
                </anki-editable>'''), '''
                    <span id="2208">asdf</span>
                    Lorem Ipsum
                ''')

    def test_extract_field_from_web_editor_extracts_field_with_mathjax(self):
        web_editor_html = """<link id="rootStyle" rel="stylesheet" href="./_anki/css/editable.css"><style id="userBase"></style><anki-editable contenteditable="true" class="svelte-18uwveo"><anki-frame block="false" data-frames="anki-mathjax"><frame-start data-frames="anki-mathjax">\u200a</frame-start><anki-mathjax focusonmount="" data-mathjax="123" style="white-space: normal;" contenteditable="false" decorated="true"><img src="data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%223.394ex%22%20height%3D%221.557ex%22%20role%3D%22img%22%20focusable%3D%22false%22%20viewBox%3D%220%20-666%201500%20688%22%20xmlns%3Axlink%3D%22http%3A%2F%2Fwww.w3.org%2F1999%2Fxlink%22%20aria-hidden%3D%22true%22%20style%3D%22vertical-align%3A%20-0.05ex%3B%22%3E%3Cstyle%3Esvg%20%7B%20color%3A%20white%3B%20fill%3A%20white%3B%20font-size%3A%2020px%3B%20%7D%3B%3C%2Fstyle%3E%3Cdefs%3E%3Cpath%20id%3D%22MJX-1-TEX-N-31%22%20d%3D%22M213%20578L200%20573Q186%20568%20160%20563T102%20556H83V602H102Q149%20604%20189%20617T245%20641T273%20663Q275%20666%20285%20666Q294%20666%20302%20660V361L303%2061Q310%2054%20315%2052T339%2048T401%2046H427V0H416Q395%203%20257%203Q121%203%20100%200H88V46H114Q136%2046%20152%2046T177%2047T193%2050T201%2052T207%2057T213%2061V578Z%22%3E%3C%2Fpath%3E%3Cpath%20id%3D%22MJX-1-TEX-N-32%22%20d%3D%22M109%20429Q82%20429%2066%20447T50%20491Q50%20562%20103%20614T235%20666Q326%20666%20387%20610T449%20465Q449%20422%20429%20383T381%20315T301%20241Q265%20210%20201%20149L142%2093L218%2092Q375%2092%20385%2097Q392%2099%20409%20186V189H449V186Q448%20183%20436%2095T421%203V0H50V19V31Q50%2038%2056%2046T86%2081Q115%20113%20136%20137Q145%20147%20170%20174T204%20211T233%20244T261%20278T284%20308T305%20340T320%20369T333%20401T340%20431T343%20464Q343%20527%20309%20573T212%20619Q179%20619%20154%20602T119%20569T109%20550Q109%20549%20114%20549Q132%20549%20151%20535T170%20489Q170%20464%20154%20447T109%20429Z%22%3E%3C%2Fpath%3E%3Cpath%20id%3D%22MJX-1-TEX-N-33%22%20d%3D%22M127%20463Q100%20463%2085%20480T69%20524Q69%20579%20117%20622T233%20665Q268%20665%20277%20664Q351%20652%20390%20611T430%20522Q430%20470%20396%20421T302%20350L299%20348Q299%20347%20308%20345T337%20336T375%20315Q457%20262%20457%20175Q457%2096%20395%2037T238%20-22Q158%20-22%20100%2021T42%20130Q42%20158%2060%20175T105%20193Q133%20193%20151%20175T169%20130Q169%20119%20166%20110T159%2094T148%2082T136%2074T126%2070T118%2067L114%2066Q165%2021%20238%2021Q293%2021%20321%2074Q338%20107%20338%20175V195Q338%20290%20274%20322Q259%20328%20213%20329L171%20330L168%20332Q166%20335%20166%20348Q166%20366%20174%20366Q202%20366%20232%20371Q266%20376%20294%20413T322%20525V533Q322%20590%20287%20612Q265%20626%20240%20626Q208%20626%20181%20615T143%20592T132%20580H135Q138%20579%20143%20578T153%20573T165%20566T175%20555T183%20540T186%20520Q186%20498%20172%20481T127%20463Z%22%3E%3C%2Fpath%3E%3C%2Fdefs%3E%3Cg%20stroke%3D%22currentColor%22%20fill%3D%22currentColor%22%20stroke-width%3D%220%22%20transform%3D%22scale(1%2C-1)%22%3E%3Cg%20data-mml-node%3D%22math%22%3E%3Cg%20data-mml-node%3D%22mn%22%3E%3Cuse%20data-c%3D%2231%22%20xlink%3Ahref%3D%22%23MJX-1-TEX-N-31%22%3E%3C%2Fuse%3E%3Cuse%20data-c%3D%2232%22%20xlink%3Ahref%3D%22%23MJX-1-TEX-N-32%22%20transform%3D%22translate(500%2C0)%22%3E%3C%2Fuse%3E%3Cuse%20data-c%3D%2233%22%20xlink%3Ahref%3D%22%23MJX-1-TEX-N-33%22%20transform%3D%22translate(1000%2C0)%22%3E%3C%2Fuse%3E%3C%2Fg%3E%3C%2Fg%3E%3C%2Fg%3E%3C%2Fsvg%3E" class="mathjax svelte-npojru" alt="Mathjax" title="" data-anki="mathjax" data-uuid="e3a63161-b194-4589-82f3-2181326ed986" style="--vertical-center:-2px; --font-size:20px;"></anki-mathjax><frame-end data-frames="anki-mathjax">\u200a</frame-end></anki-frame>&nbsp;2<span id="6715">3</span></anki-editable> """
        self.assertEqual(
            extract_field_from_web_editor(web_editor_html),
            '''<anki-frame block="false" data-frames="anki-mathjax"><frame-start data-frames="anki-mathjax">\u200a</frame-start><anki-mathjax focusonmount="" data-mathjax="123" style="white-space: normal;" contenteditable="false" decorated="true"><img src="data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%223.394ex%22%20height%3D%221.557ex%22%20role%3D%22img%22%20focusable%3D%22false%22%20viewBox%3D%220%20-666%201500%20688%22%20xmlns%3Axlink%3D%22http%3A%2F%2Fwww.w3.org%2F1999%2Fxlink%22%20aria-hidden%3D%22true%22%20style%3D%22vertical-align%3A%20-0.05ex%3B%22%3E%3Cstyle%3Esvg%20%7B%20color%3A%20white%3B%20fill%3A%20white%3B%20font-size%3A%2020px%3B%20%7D%3B%3C%2Fstyle%3E%3Cdefs%3E%3Cpath%20id%3D%22MJX-1-TEX-N-31%22%20d%3D%22M213%20578L200%20573Q186%20568%20160%20563T102%20556H83V602H102Q149%20604%20189%20617T245%20641T273%20663Q275%20666%20285%20666Q294%20666%20302%20660V361L303%2061Q310%2054%20315%2052T339%2048T401%2046H427V0H416Q395%203%20257%203Q121%203%20100%200H88V46H114Q136%2046%20152%2046T177%2047T193%2050T201%2052T207%2057T213%2061V578Z%22%3E%3C%2Fpath%3E%3Cpath%20id%3D%22MJX-1-TEX-N-32%22%20d%3D%22M109%20429Q82%20429%2066%20447T50%20491Q50%20562%20103%20614T235%20666Q326%20666%20387%20610T449%20465Q449%20422%20429%20383T381%20315T301%20241Q265%20210%20201%20149L142%2093L218%2092Q375%2092%20385%2097Q392%2099%20409%20186V189H449V186Q448%20183%20436%2095T421%203V0H50V19V31Q50%2038%2056%2046T86%2081Q115%20113%20136%20137Q145%20147%20170%20174T204%20211T233%20244T261%20278T284%20308T305%20340T320%20369T333%20401T340%20431T343%20464Q343%20527%20309%20573T212%20619Q179%20619%20154%20602T119%20569T109%20550Q109%20549%20114%20549Q132%20549%20151%20535T170%20489Q170%20464%20154%20447T109%20429Z%22%3E%3C%2Fpath%3E%3Cpath%20id%3D%22MJX-1-TEX-N-33%22%20d%3D%22M127%20463Q100%20463%2085%20480T69%20524Q69%20579%20117%20622T233%20665Q268%20665%20277%20664Q351%20652%20390%20611T430%20522Q430%20470%20396%20421T302%20350L299%20348Q299%20347%20308%20345T337%20336T375%20315Q457%20262%20457%20175Q457%2096%20395%2037T238%20-22Q158%20-22%20100%2021T42%20130Q42%20158%2060%20175T105%20193Q133%20193%20151%20175T169%20130Q169%20119%20166%20110T159%2094T148%2082T136%2074T126%2070T118%2067L114%2066Q165%2021%20238%2021Q293%2021%20321%2074Q338%20107%20338%20175V195Q338%20290%20274%20322Q259%20328%20213%20329L171%20330L168%20332Q166%20335%20166%20348Q166%20366%20174%20366Q202%20366%20232%20371Q266%20376%20294%20413T322%20525V533Q322%20590%20287%20612Q265%20626%20240%20626Q208%20626%20181%20615T143%20592T132%20580H135Q138%20579%20143%20578T153%20573T165%20566T175%20555T183%20540T186%20520Q186%20498%20172%20481T127%20463Z%22%3E%3C%2Fpath%3E%3C%2Fdefs%3E%3Cg%20stroke%3D%22currentColor%22%20fill%3D%22currentColor%22%20stroke-width%3D%220%22%20transform%3D%22scale(1%2C-1)%22%3E%3Cg%20data-mml-node%3D%22math%22%3E%3Cg%20data-mml-node%3D%22mn%22%3E%3Cuse%20data-c%3D%2231%22%20xlink%3Ahref%3D%22%23MJX-1-TEX-N-31%22%3E%3C%2Fuse%3E%3Cuse%20data-c%3D%2232%22%20xlink%3Ahref%3D%22%23MJX-1-TEX-N-32%22%20transform%3D%22translate(500%2C0)%22%3E%3C%2Fuse%3E%3Cuse%20data-c%3D%2233%22%20xlink%3Ahref%3D%22%23MJX-1-TEX-N-33%22%20transform%3D%22translate(1000%2C0)%22%3E%3C%2Fuse%3E%3C%2Fg%3E%3C%2Fg%3E%3C%2Fg%3E%3C%2Fsvg%3E" class="mathjax svelte-npojru" alt="Mathjax" title="" data-anki="mathjax" data-uuid="e3a63161-b194-4589-82f3-2181326ed986" style="--vertical-center:-2px; --font-size:20px;"></anki-mathjax><frame-end data-frames="anki-mathjax">\u200a</frame-end></anki-frame>&nbsp;2<span id="6715">3</span>'''
        )
