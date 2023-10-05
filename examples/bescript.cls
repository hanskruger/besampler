\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{bescript}[2013/10/01 Bloco Esperanca Script Class]

%% Article options
\DeclareOption{12pt}{
  \PassOptionsToClass{\CurrentOption}{article}
}

%% Article options
\DeclareOption{a4paper}{
  \PassOptionsToClass{\CurrentOption}{article}
}

%% Custom package options

%% Fallback
\DeclareOption*{
  \ClassWarning{bescript}{Unknown option '\CurrentOption'}
}

%% Execute default options
\ExecuteOptions{12pt,a4paper}

%% Process given options
\ProcessOptions\relax

%% Load base
\LoadClass[a4paper,12pt]{article}
%% Load additional packages and commands.
%\RequirePackage{custom}

\RequirePackage{graphicx}
\RequirePackage[utf8]{inputenc}
\RequirePackage{url}
\RequirePackage{colortbl,xcolor}
\RequirePackage[top=25mm,bottom=15mm,right=15mm,left=15mm]{geometry}
\RequirePackage{fancyhdr}
\RequirePackage[colorlinks,linkcolor={black},citecolor={black},urlcolor={black}]{hyperref}
\RequirePackage{background}

\backgroundsetup{position=current page.south, anchor=above,opacity=0.1, vshift=5pt,hshift=20pt,angle=0,contents={\includegraphics[scale=0.5]{Bloco_Esperanca.png}}}

\definecolor{Gray}{gray}{0.85}

\newcounter{measure}
\setcounter{measure}{1}
\def\m{\themeasure\stepcounter{measure}}

\newcommand{\mhead}[1]{\multicolumn{4}{l|}{\m{} #1}}

\newcolumntype{A}[0]{>{}p{5em}}
\newcolumntype{C}[0]{>{\centering\arraybackslash}p{2.5em}}
\newcolumntype{D}[0]{>{\columncolor{Gray}\centering\arraybackslash}p{2em}}

\newenvironment{staffline}{\begingroup
\small
\setlength{\tabcolsep}{0pt} % Default value: 6pt
%^\renewcommand{\arraystretch}{1.5} % Default value: 1
\begin{tabular}{A|CDCD|CDCD|CDCD|CDCD|}
}{
\end{tabular}
\endgroup
\vspace{1ex}
}
\sloppy

\renewcommand{\familydefault}{\ttdefault}

\newcommand{\samba}[4] {
\clearpage
\phantomsection
\addcontentsline{toc}{section}{#3}
\includepdf[pages=#1, pagecommand=\thispagestyle{plain}]{#2}}

\newcommand{\chapterx}[1] {
\clearpage\phantomsection
\addcontentsline{toc}{chapter}{#1}
}

\newcommand{\sectionx}[1] {
\clearpage\phantomsection
\addcontentsline{toc}{section}{#1}
}

\newcommand{\kw}[1] {\textit{#1}}
\newcommand{\decl}[1] {\textbf{#1}}
\newcommand{\xref}[1] {\ref{#1}}


\makeatletter
\renewcommand{\maketitle}{%
\vspace*{1cm}
\begin{center}
{\Huge \@title}
\end{center}
\vspace*{1cm}
}
\makeatother

\makeatletter
\fancypagestyle{plain}{%
  \renewcommand{\headrulewidth}{0pt}%
  \fancyfoot[C]{\tiny © 2023 Urheberrechtlich geschütztes Material. Bloco Esperença e.V., Dresden}%
}
\makeatother
\pagestyle{plain}
%\thispagestyle{empty}


\endinput

