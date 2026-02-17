$pdf_mode = 4;
$dvi_mode = $postscript_mode = 0;
$out_dir = "artifacts";

$lualatex = 'lualatex -interaction=nonstopmode -synctex=1 --shell-escape %O %S;';
