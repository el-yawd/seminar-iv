$pdf_mode = 1;            # pdflatex (use 4 for lualatex, 5 for xelatex)
$out_dir = 'build';
$bibtex_use = 2;          # run bibtex as needed, clean .bbl on -C
$pdflatex = 'pdflatex -interaction=nonstopmode -halt-on-error -synctex=1 -file-line-error %O %S';
$pdf_previewer = 'zathura %S';
