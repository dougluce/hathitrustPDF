import pytest
import importlib
import responses
import shutil

# A trimmed-down version of the HTML document that contains info about
# the number of pages
root_doc="""
        <meta property="og:title" content="Resumo chronologico para a história do Ceará.  " />
        <section class="d--reader">
          <div id="reader" class="d--reader--container" tabindex="0">
            <section class="d--reader--viewer" data-has-ocr="true" data-allow-full-download="false" data-reading-order="left-to-right" data-total-seq="3" data-default-seq="9" data-first-seq="1" data-default-height="1075" data-default-width="680" data-htid="txu.059173023561817"></section>
          </div>
        </section>
"""

# A proper PDF template for each of the pages in the document.
page_template="""%PDF-1.7
%âã
1 0 obj               % The list of pages.
<<
  /Type /Pages        % Define the pages in the file.
  /Count 1            % There's just the one.
  /Kids [2 0 R]       % It's defined in object 2.
>>
endobj
2 0 obj               % Definition of our single, simple page
<<
  /Type /Page
  /Parent 1 0 R
  /Resources <<
    /Font <<
      /F0 <<
        /Type /Font
        /BaseFont /Times-Italic
        /Subtype /Type1
      >>
    >>
  >>
  /MediaBox [0 0 600 850]
  /Contents 3 0 R
>>
3 0 obj               % Contents of the page
<< /Length 314 >>
stream
BT                    % Begin text object
  /F0 180 Tf          % Use super-tall 180-point Times-Italic
  30 Tz 40 Tc         % Smush it narrow and space it out a bit
  60 400 Td           % Stick the text about in the middle
  (Page Number {}) Tj  % It'll be the page number
ET                    % End text object
endstream
endobj
4 0 obj               % The page catalog
<<
  /Type /Catalog
  /Pages 1 0 R
>>
endobj
xref
0 0
trailer
<<
  /Root 4 0 R
>>
startxref
972
%%EOF
"""

class TestHathi:
  @responses.activate
  def test_simple(self):
    # Fake out the web server sending the root doc.
    responses.add(responses.GET, 'https://babel.hathitrust.org/cgi/pt?id=txu.059173023561817', body=root_doc)
    # Fake out three http calls, one for each of the three pages in the fake root doc.
    for page_number in range(1, 4):
      responses.add(responses.GET, f'https://babel.hathitrust.org/cgi/imgsrv/download/pdf?id=txu.059173023561817;orient=0;size=100;seq={page_number};attachment=0',
                    body=page_template.format(page_number))

    # Load and run the main script. It'll fetch the faked data above.
    self.main = importlib.import_module('hathitrustPDF.__main__')

    # Pull in the entire file (it should be short, about 2kb).
    with open(self.main.fout.name, 'rb') as f:
      output_doc = str(f.read())

    # Find each page number string in the combined ocument
    assert 'Page Number 1' in output_doc
    assert 'Page Number 2' in output_doc
    assert 'Page Number 3' in output_doc

  # The test run creates a directory containing the output and working
  # files. Clean it up after.
  @pytest.fixture(autouse=True)
  def working_dir(self):
    yield
    shutil.rmtree(self.main.path_folder)

