{
  description = "LaTeX environment for seminar-iv";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        # scheme-medium covers most needs; add extra collections/packages here.
        tex = pkgs.texlive.combine {
          inherit (pkgs.texlive)
            scheme-medium
            collection-langportuguese
            collection-latexextra
            collection-fontsrecommended
            collection-bibtexextra
            collection-mathscience
            libertine
            fontaxes
            mweights
            newtx
            biber
            latexmk
            latexindent
            chktex;
        };
      in
      {
        devShells.default = pkgs.mkShell {
          packages = [
            tex
            pkgs.texlab   # LSP for editors
            pkgs.ltex-ls-plus  # grammar/spell checking LSP (pt-BR / en)
            pkgs.zathura  # PDF viewer with SyncTeX + auto-reload
          ];
        };

        # `nix build` -> result/main.pdf
        packages.default = pkgs.stdenvNoCC.mkDerivation {
          name = "seminar-iv-pdf";
          src = self;
          nativeBuildInputs = [ tex ];
          buildPhase = ''
            export HOME=$TMPDIR
            export SOURCE_DATE_EPOCH=${toString self.lastModified}
            latexmk main.tex
          '';
          installPhase = ''
            mkdir -p $out
            cp build/main.pdf $out/
          '';
        };
      });
}
