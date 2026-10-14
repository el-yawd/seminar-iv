% ============================================================
% Universidade Federal de Itajubá
% Instituto de Matemática e Computação
%
% Classe LaTeX para artigos da disciplina XRSC10
% Curso de Computação de Borda
%
% Professor: Pioli
% Autor do template: Laércio Pioli
%
% Última atualização: 07/10/2026
% ============================================================

\NeedsTeXFormat{LaTeX2e}

\ProvidesClass{imc}[2026/10/07 v1.2 - Laercio Pioli]


% ============================================================
% CLASSE BASE
% ============================================================

\LoadClass[
    10pt,
    a4paper,
    twocolumn,
    twoside
]{article}


% ============================================================
% PACOTES
% ============================================================

\RequirePackage{afterpage}

\RequirePackage[
    ruled,
    linesnumbered,
    commentsnumbered,
    portuguese,
    onelanguage
]{algorithm2e}

\RequirePackage{amsmath}
\RequirePackage{amssymb}
\RequirePackage{amsthm}

\RequirePackage{array}

\RequirePackage[brazilian]{babel}

\RequirePackage[font=small]{caption}

\RequirePackage[
    table,
    x11names
]{xcolor}

\RequirePackage[inline]{enumitem}

\RequirePackage{float}

\RequirePackage{ifthen}

\RequirePackage{fancyhdr}

\RequirePackage[T1]{fontenc}

\RequirePackage[
    top=20mm,
    bottom=20mm,
    left=15mm,
    right=15mm
]{geometry}

\RequirePackage{graphicx}

\RequirePackage{hyphenat}

\RequirePackage[hyphens]{url}

\RequirePackage{lastpage}

\RequirePackage[
    tt=false,
    type1=true
]{libertine}

\RequirePackage{listings}

\RequirePackage{longtable}

\RequirePackage{lscape}

\RequirePackage{multirow}

\RequirePackage{natbib}

\RequirePackage[libertine]{newtxmath}

\RequirePackage{pdflscape}

\RequirePackage{quoting}

\RequirePackage{rotating}

\RequirePackage{setspace}

\RequirePackage{subfigure}

\RequirePackage[absolute]{textpos}

\RequirePackage[normalem]{ulem}

\RequirePackage{eso-pic}

\RequirePackage[
    breaklinks,
    bookmarksnumbered=true,
    bookmarksopen=true,
    colorlinks=true,
    linkcolor=azul,
    citecolor=azul,
    filecolor=azul,
    urlcolor=azul,
    hyperindex=true,
    pagebackref=false
]{hyperref}


% ============================================================
% CORES
% ============================================================

\definecolor{azul}{rgb}{0,0,1.0}


% ============================================================
% INFORMAÇÕES DO ARTIGO
% ============================================================

% ------------------------------------------------------------
% Ano
% ------------------------------------------------------------

\newcommand*{\ano}[1]{
    \gdef\@ano{#1}
}


% ------------------------------------------------------------
% Mês
% ------------------------------------------------------------

\newcommand*{\mes}[1]{
    \gdef\@mes{#1}
}


% ------------------------------------------------------------
% Autor A
% ------------------------------------------------------------

\newcommand*{\autorNomeA}[1]{
    \gdef\@autorNomeA{#1}
}

\newcommand*{\autorSobrenomeA}[1]{
    \gdef\@autorSobrenomeA{#1}
}

\newcommand*{\emailAutorA}[1]{
    \gdef\@emailAutorA{#1}
}


% ------------------------------------------------------------
% Autor B
% ------------------------------------------------------------

\newcommand*{\autorNomeB}[1]{
    \gdef\@autorNomeB{#1}
}

\newcommand*{\autorSobrenomeB}[1]{
    \gdef\@autorSobrenomeB{#1}
}

\newcommand*{\emailAutorB}[1]{
    \gdef\@emailAutorB{#1}
}


% ------------------------------------------------------------
% Título
% ------------------------------------------------------------

\newcommand*{\titulo}[1]{
    \gdef\@titulo{#1}
}



% ------------------------------------------------------------
% linkLatex
% ------------------------------------------------------------

\newcommand*{\linkLatex}[1]{
    \gdef\@linkLatex{#1}
}


% ------------------------------------------------------------
% Disciplina
% ------------------------------------------------------------

\newcommand*{\disciplina}[1]{
    \gdef\@disciplina{#1}
}


% ------------------------------------------------------------
% Professor
% ------------------------------------------------------------

\newcommand*{\professor}[1]{
    \gdef\@professor{#1}
}


% ------------------------------------------------------------
% Palavras-chave
% ------------------------------------------------------------

\newcommand*{\palavraChaveA}[1]{
    \gdef\@palavraChaveA{#1}
}

\newcommand*{\palavraChaveB}[1]{
    \gdef\@palavraChaveB{#1}
}

\newcommand*{\palavraChaveC}[1]{
    \gdef\@palavraChaveC{#1}
}

\newcommand*{\palavraChaveD}[1]{
    \gdef\@palavraChaveD{#1}
}

\newcommand*{\palavraChaveE}[1]{
    \gdef\@palavraChaveE{#1}
}


% ============================================================
% INFORMAÇÕES INSTITUCIONAIS
% ============================================================

\newcommand{\instituto}{
    Instituto de Matemática e Computação
}

\newcommand{\instituicao}{
    Universidade Federal de Itajubá
}

\newcommand{\sigla}{
    UNIFEI
}

\newcommand{\curso}{
    Curso de Computação de Borda
}


% ============================================================
% OPÇÕES DA CLASSE
% ============================================================

\DeclareOption*{}

\ProcessOptions


% ============================================================
% CONFIGURAÇÕES GERAIS
% ============================================================

\pdfminorversion=7

\everymath{\displaystyle}

\frenchspacing

\sloppy

\raggedbottom


% ============================================================
% CONFIGURAÇÃO DE FLOATS
% ============================================================

\setcounter{topnumber}{8}

\setcounter{bottomnumber}{8}

\setcounter{totalnumber}{8}


% ============================================================
% ESPAÇAMENTO
% ============================================================

\setlength{\columnsep}{13pt}

\setlength{\parindent}{7mm}


% ============================================================
% CABEÇALHO E RODAPÉ
% ============================================================

\pagestyle{fancy}

\renewcommand{\sectionmark}[1]{
    \markright{\thesection.\ #1}
}

\renewcommand{\headrulewidth}{0.5pt}

\renewcommand{\footrulewidth}{0pt}

\fancyhf{}

\setlength{\headheight}{16pt}


\if@twoside

    \fancyhead[LE,RO]{
        \thepage
    }

    \fancyhead[LO]{
        \slshape
        \@autorNomeA\space\@autorSobrenomeA%
        \ifthenelse{\equal{\@autorNomeB}{}}
        {}
        {
            ,~\@autorNomeB\space\@autorSobrenomeB%
        }
    }

    \fancyhead[RE]{
        \slshape
        \@titulo
    }

\else

    \fancyhead[RO]{
        \thepage
    }

    \fancyhead[LO]{
        \slshape
        \@titulo
    }

\fi


% ============================================================
% CONFIGURAÇÃO DO LISTINGS
% ============================================================

\lstset{
    numbers=left,
    stepnumber=1,
    firstnumber=1,
    numberstyle=\scriptsize\textbf,
    extendedchars=true,
    breaklines=true,
    frame=tb,
    basicstyle=\small,
    stringstyle=\ttfamily,
    showstringspaces=false,
    xleftmargin=5mm
}


% ============================================================
% FORMATAÇÃO DAS SEÇÕES
% ============================================================

\def\@seccntformat#1{%
    {\csname the#1\endcsname\;}
}


\renewcommand\section{%
    \@startsection
    {section}
    {1}
    {\z@}
    {-3.5ex \@plus -1ex \@minus -.2ex}
    {2.3ex \@plus .2ex}
    {\large\bfseries}%
}


\renewcommand{\subsection}{%
    \@startsection
    {subsection}
    {2}
    {\z@}
    {-3.25ex\@plus -1ex \@minus -.2ex}
    {1.5ex \@plus .2ex}
    {\large\bfseries}%
}


\renewcommand{\subsubsection}{%
    \@startsection
    {subsubsection}
    {3}
    {\z@}
    {-3.25ex\@plus -1ex \@minus -.2ex}
    {1.5ex \@plus .2ex}
    {\large\bfseries}%
}


% ============================================================
% PÁGINA INICIAL DO ARTIGO
% ============================================================

\newcommand{\criaPaginaInicialArtigo}
{

    % ========================================================
    % FUNDO / LOGOS INSTITUCIONAIS
    % ========================================================

    \AddToShipoutPictureBG*{
        \includegraphics[
            width=\paperwidth,
            height=\paperheight
        ]{./config/logo.pdf}
    }


    % ========================================================
    % CONTEÚDO DA PRIMEIRA PÁGINA
    % ========================================================

    \twocolumn[

        \vspace*{25mm}


        % ----------------------------------------------------
        % TÍTULO
        % ----------------------------------------------------

        {
            \LARGE
            \centering

            \@titulo

            \par

            \vspace*{\baselineskip}
        }



        % ----------------------------------------------------
        % AUTORES
        % ----------------------------------------------------

        {
            \Large
            \centering

            \@autorNomeA\space\@autorSobrenomeA%

            \ifthenelse{\equal{\@autorNomeB}{}}
            {

                \par

                \textit{
                    \normalsize
                    \@emailAutorA
                }

            }
            {

                ,\space
                \@autorNomeB\space\@autorSobrenomeB%

                \par

                \textit{
                    \normalsize
                    \@emailAutorA,\space
                    \@emailAutorB
                }

            }

            \par

            \vspace*{9pt}
        }


        % ----------------------------------------------------
        % DISCIPLINA
        % ----------------------------------------------------

        {
            \centering
            \textit{Disciplina:}\space
            \@disciplina
            \par
        }


        % ----------------------------------------------------
        % PROFESSOR
        % ----------------------------------------------------

        {
            \centering
            \textit{Prof.}\space
            \@professor
            \par
        }


        \vspace*{\baselineskip}


        % ----------------------------------------------------
        % RESUMO
        % ----------------------------------------------------

        {

            \hrulefill

            \vspace*{4pt}

            \textbf{
                \MakeUppercase{\resumo}
            }

            \par

            \input{./elemtextuais/abstract.tex}

            \par

            \vspace*{-2pt}

            \hrulefill

            \par


            % ------------------------------------------------
            % PALAVRAS-CHAVE
            % ------------------------------------------------

            \noindent

            \textbf{Palavras-chave:}\space

            \@palavraChaveA;
            \space\@palavraChaveB;
            \space\@palavraChaveC

            \ifthenelse{\equal{\@palavraChaveD}{}}
            {}
            {
                ;\space\@palavraChaveD
            }

            \ifthenelse{\equal{\@palavraChaveE}{}}
            {}
            {
                ;\space\@palavraChaveE
            }

            \par

        }

        \vspace*{12pt}

    ]
     % ========================================================
    % CABEÇALHO INSTITUCIONAL
    %
    % UNIVERSIDADE FEDERAL DE ITAJUBÁ
    %INSTITUTO DE MATEMÁTICA E COMPUTAÇÃO
    %CURSO DE COMPUTAÇÃO DE BORDA
    % ========================================================

    % 
    \AddToShipoutPictureFG*{
    
        \AtPageUpperLeft{
    
            \put(47mm,-27mm){
    
                \makebox[120mm][c]{
    
                    \begin{minipage}{120mm}
    
                        \centering
    
                        {\normalsize
                            \MakeUppercase{\instituicao}
                        }
    
                        \par
                        \vspace*{4pt}
    
                        {\normalsize
                            \MakeUppercase{\instituto}
                        }
    
                        \par
                        \vspace*{4pt}
    
                        {\normalsize
                            \MakeUppercase{\curso}
                        }
    
                    \end{minipage}
    
                }
    
            }
    
        }
    
    }

    % ========================================================
    % CABEÇALHO INSTITUCIONAL
    %
    % Este é o texto que estava desaparecendo.
    % Ele fica na MESMA página do título.
    % ========================================================

    % ========================================================
    % RODAPÉ INSTITUCIONAL
    % ========================================================

    \begin{textblock*}{88.1mm}(15mm,276.5mm)

        \begin{center}

            \hrulefill

        \end{center}

        \begin{flushleft}

            \vspace*{-10pt}

            {
                \large
                \textcopyright~IMC-UNIFEI -
                \@mes\space de\space\@ano
            }

        \end{flushleft}

    \end{textblock*}

}


% ============================================================
% MAKETITLE
% ============================================================

% IMPORTANTE:
%
% Não colocar \hypersetup dentro deste comando.
% A versão anterior causava o erro:
%
% Paragraph ended before \kv@processor@default was complete.
%
% O \maketitle deve apenas chamar a página inicial.


\renewcommand{\maketitle}
{
    \criaPaginaInicialArtigo
}


% ============================================================
% FIGURAS EM PAISAGEM
% ============================================================

\newenvironment{figpaisagem}
{

    \begin{figure*}

        \begin{turn}{90}

            \begin{minipage}{\textheight}

                \begin{center}

}
{

                \end{center}

            \end{minipage}

        \end{turn}

    \end{figure*}

}


% ============================================================
% TABELAS EM PAISAGEM
% ============================================================

\newenvironment{tabpaisagem}
{

    \begin{table*}

        \begin{turn}{90}

            \begin{minipage}{\textheight}

                \begin{center}

}
{

                \end{center}

            \end{minipage}

        \end{turn}

    \end{table*}

}


% ============================================================
% FIGURAS/TABELAS EM PAISAGEM
% ============================================================

\newcommand{\paisagem}[2]
{

    \ifthenelse{\equal{#1}{f}}
    {

        \begin{figure*}

            \begin{turn}{90}

                \begin{minipage}{\textheight}

                    \begin{center}

                        #2

                    \end{center}

                \end{minipage}

            \end{turn}

        \end{figure*}

    }
    {

        \begin{table*}

            \begin{turn}{90}

                \begin{minipage}{\textheight}

                    \begin{center}

                        #2

                    \end{center}

                \end{minipage}

            \end{turn}

        \end{table*}

    }

}


% ============================================================
% ELEMENTOS TEXTUAIS
% ============================================================

\AtBeginDocument
{

    \newcommand{\myabstract}{\resumo}

    \newcommand{\resumo}{Resumo}

    \renewcommand{\bibname}{Referências}

    \renewcommand{\refname}{Referências}

    \renewcommand{\figurename}{Figura}

    \renewcommand{\tablename}{Tabela}

    \renewcommand{\lstlistingname}{Código}

}
