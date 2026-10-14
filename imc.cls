% Universidade Federal de Itajuba
% Instituto de Matematica e Computacao
%
% Classe para o trabalho final da disciplina XRSC10 (Prof. Pioli), em formato de artigo.
% Derivada do modelo de artigo do IMC-UNIFEI:
% - Template: Luiz Olmes Carvalho - olmes@unifei.edu.br
% - Texto: Rafael de Magalhaes Dias Frinhani - frinhani@unifei.edu.br
%
% +-------------------------+
% | NAO ALTERE ESTE ARQUIVO |
% +-------------------------+

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{imc}[2026/10/14 XRSC10 - Trabalho Final]

\LoadClass[10pt, a4paper, twocolumn, twoside]{article}

% Pacotes padrao
\RequirePackage[ruled, linesnumbered, commentsnumbered, portuguese, onelanguage]{algorithm2e}
\RequirePackage{amsmath, amssymb, amsthm}
\RequirePackage{array}
\RequirePackage{booktabs}
\RequirePackage[brazil]{babel}
\RequirePackage[font=small]{caption}
\RequirePackage[usenames, table, x11names]{xcolor}
\RequirePackage[inline]{enumitem}
\RequirePackage{float}
\RequirePackage{ifthen}
\RequirePackage{fancyhdr}
\RequirePackage[T1]{fontenc}
\usepackage[tt=false, type1=true]{libertine} % Fonte do documento (igual a classe oficial do IMC)
\usepackage[libertine]{newtxmath} % Fonte matematica (igual a classe oficial do IMC)
\RequirePackage[top=20mm, bottom=20mm, left=15mm, right=15mm]{geometry}
\RequirePackage{graphicx}
\RequirePackage[hyphens]{url}
\RequirePackage{listings}
\RequirePackage[round]{natbib}
\RequirePackage{setspace}
\RequirePackage[absolute]{textpos}
\RequirePackage{eso-pic}
\RequirePackage{tikz}
\usetikzlibrary{positioning, arrows.meta, shapes.geometric, fit}
\RequirePackage[breaklinks, bookmarksnumbered=true, bookmarksopen=true, colorlinks=true, linkcolor=azul, citecolor=azul, filecolor=azul, urlcolor=azul]{hyperref}

\definecolor{azul}{RGB}{0, 0, 128}

% Variaveis do trabalho (preenchidas em configuracao.tex)
\newcommand*{\ano}[1]{\gdef\@ano{#1}}
\newcommand*{\mes}[1]{\gdef\@mes{#1}}
\newcommand*{\titulo}[1]{\gdef\@titulo{#1}\gdef\@tituloCurto{#1}}
\newcommand*{\tituloCurto}[1]{\gdef\@tituloCurto{#1}} % opcional: titulo no cabecalho
\newcommand*{\autorNomeA}[1]{\gdef\@autorNomeA{#1}}
\newcommand*{\autorSobrenomeA}[1]{\gdef\@autorSobrenomeA{#1}}
\newcommand*{\emailAutorA}[1]{\gdef\@emailAutorA{#1}}
\newcommand*{\autorNomeB}[1]{\gdef\@autorNomeB{#1}}
\newcommand*{\autorSobrenomeB}[1]{\gdef\@autorSobrenomeB{#1}}
\newcommand*{\emailAutorB}[1]{\gdef\@emailAutorB{#1}}
\newcommand*{\disciplina}[1]{\gdef\@disciplina{#1}}
\newcommand*{\professor}[1]{\gdef\@professor{#1}}
\newcommand*{\palavraChaveA}[1]{\gdef\@palavraChaveA{#1}}
\newcommand*{\palavraChaveB}[1]{\gdef\@palavraChaveB{#1}}
\newcommand*{\palavraChaveC}[1]{\gdef\@palavraChaveC{#1}}
\newcommand*{\palavraChaveD}[1]{\gdef\@palavraChaveD{#1}}
\newcommand*{\palavraChaveE}[1]{\gdef\@palavraChaveE{#1}}

\newcommand{\instituto}{Instituto de Matemática e Computação}
\newcommand{\instituicao}{Universidade Federal de Itajubá}
\newcommand{\curso}{Curso de Computação de Borda}

\pdfminorversion=7
\frenchspacing
\sloppy
\raggedbottom

\setcounter{topnumber}{8}
\setcounter{bottomnumber}{8}
\setcounter{totalnumber}{8}

\setlength{\columnsep}{13pt}
\setlength{\parindent}{7mm}

% Cabecalhos
\pagestyle{fancy}
\renewcommand{\sectionmark}[1]{\markright{\thesection.\ #1}}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}
\fancyhf{}
\setlength{\headheight}{16pt}
\fancyhead[LE, RO]{\thepage}
\fancyhead[LO]{\slshape\@autorNomeA\space\@autorSobrenomeA%
    \ifthenelse{\equal{\@autorNomeB}{}}{}{,~\@autorNomeB\space\@autorSobrenomeB}%
}
\fancyhead[RE]{\slshape\@tituloCurto}
\fancypagestyle{primeira}{%
    \fancyhf{}%
    \fancyhead[LO]{\slshape\@autorNomeA\space\@autorSobrenomeA%
        \ifthenelse{\equal{\@autorNomeB}{}}{}{,~\@autorNomeB\space\@autorSobrenomeB}}%
    \fancyhead[RO]{\thepage}%
}

\lstset{
    numbers=left,
    stepnumber=1,
    firstnumber=1,
    numberstyle=\scriptsize\ttfamily,
    extendedchars=true,
    breaklines=true,
    frame=tb,
    basicstyle=\scriptsize\ttfamily,
    columns=fullflexible,
    keepspaces=true,
    stringstyle=\ttfamily,
    keywordstyle=\bfseries,
    showstringspaces=false,
    xleftmargin=5mm,
    literate={á}{{\'a}}1 {ã}{{\~a}}1 {ç}{{\c c}}1 {é}{{\'e}}1 {ê}{{\^e}}1 {í}{{\'i}}1 {ó}{{\'o}}1 {õ}{{\~o}}1 {ú}{{\'u}}1 {μ}{{$\mu$}}1 {α}{{$\alpha$}}1
}

% Secoes
\def\@seccntformat#1{{\csname the#1\endcsname\;}}
\renewcommand\section{%
    \@startsection{section}{1}{\z@}%
    {-3.5ex \@plus -1ex \@minus -.2ex}%
    {2.3ex \@plus.2ex}%
    {\large\bfseries}%
}
\renewcommand{\subsection}{%
    \@startsection{subsection}{2}{\z@}%
    {-3.25ex\@plus -1ex \@minus -.2ex}%
    {1.5ex \@plus .2ex}%
    {\large\bfseries}%
}
\renewcommand{\subsubsection}{%
    \@startsection{subsubsection}{3}{\z@}%
    {-3.25ex\@plus -1ex \@minus -.2ex}%
    {1.5ex \@plus .2ex}%
    {\normalsize\bfseries}%
}

% Primeira pagina: cabecalho institucional, titulo, autoria e resumo
\newcommand{\criaPaginaInicialArtigo}{%
    \pagenumbering{arabic}%
    \thispagestyle{primeira}%
    \AddToShipoutPictureBG*{\includegraphics[height=\paperheight]{./config/unifei-imc.pdf}}%
    \twocolumn[
        \vspace*{22mm}
        {\LARGE\centering\@titulo\par\vspace*{\baselineskip}}
        {\Large\centering\@autorNomeA\space\@autorSobrenomeA%
            \ifthenelse{\equal{\@autorNomeB}{}}%
            {\par{\textit{\normalsize\@emailAutorA}}}%
            {,\space\@autorNomeB\space\@autorSobrenomeB%
                \par\textit{\normalsize\@emailAutorA,\space\@emailAutorB}}%
            \par\vspace*{9pt}%
        }%
        {\centering\textit{Disciplina:}\space\@disciplina\par}
        {\centering\textit{Prof.}\space\@professor\par}
        \vspace*{\baselineskip}
        {
            \hrulefill

            {\vspace*{4pt}\noindent\textbf{\MakeUppercase{Resumo}}\par}
            {\noindent\input{./elemtextuais/resumo.tex}\par}
            \vspace*{-2pt}
            \hrulefill
            {
                \par\noindent\textbf{Palavras-chave:}\par\noindent\@palavraChaveA\space;\space\@palavraChaveB\space;\space\@palavraChaveC%
                \ifthenelse{\equal{\@palavraChaveD}{}}{}{\space;\space\@palavraChaveD}%
                \ifthenelse{\equal{\@palavraChaveE}{}}{}{\space;\space\@palavraChaveE}%
            }
        }
        \vspace*{14pt}
    ]
    % Cabecalho institucional e rodape desenhados em primeiro plano: como blocos
    % do textpos, ficavam sob o fundo opaco de unifei-imc.pdf e nao apareciam.
    \AddToShipoutPictureFG*{%
        \AtPageUpperLeft{\put(\LenToUnit{45mm},\LenToUnit{-21mm}){\parbox[t]{120mm}{\centering\normalsize
            \MakeUppercase{\instituicao}\\[3pt]
            \MakeUppercase{\instituto}\\[3pt]
            \MakeUppercase{\curso}}}}%
        \AtPageLowerLeft{\put(\LenToUnit{15mm},\LenToUnit{14mm}){\parbox[b]{88.1mm}{%
            \hrule\vspace*{3pt}
            {\small\textcopyright~IMC-UNIFEI - \@mes\space de\space\@ano}}}}%
    }%
}

\renewcommand{\maketitle}{%
    \hypersetup{%
        pdftitle={\@titulo},
        pdfauthor={\@autorNomeA\space\@autorSobrenomeA\space\@autorNomeB\space\@autorSobrenomeB},
        pdfsubject={\@disciplina},
        pdfkeywords={\@palavraChaveA, \@palavraChaveB, \@palavraChaveC, \@palavraChaveD, \@palavraChaveE},
    }%
    \criaPaginaInicialArtigo%
}

\AtBeginDocument{%
    \renewcommand{\figurename}{Figura}%
    \renewcommand{\tablename}{Tabela}%
    \renewcommand{\lstlistingname}{Código}%
    \renewcommand{\refname}{Referências}%
}
