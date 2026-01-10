{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/25.11";
  };

  outputs = {nixpkgs, ...}: let
    systems = ["x86_64-linux" "aarch64-linux"];
  in {
    packages = nixpkgs.lib.genAttrs systems (system: let
      pkgs = import nixpkgs {inherit system;};
    in {
      default = pkgs.stdenv.mkDerivation {
        pname = "jumper";
        version = "0.0.1";
        src = pkgs.nix-gitignore.gitignoreSource [] ./.;
        nativeBuildInputs = with pkgs; [
          makeWrapper
        ];
        buildInputs = with pkgs; [
          bash
          python313
          python313Packages.boto3
        ];

        installPhase = ''
          mkdir -p $out/bin $out/lib
          cp -r . $out/lib/jumper
          tee  $out/bin/jumper <<EOF
            #!${pkgs.bash}/bin/bash
            ${pkgs.python313}/bin/python $out/lib/jumper
          EOF
          chmod +x $out/bin/jumper
          wrapProgram $out/bin/jumper --prefix PATH : ${pkgs.lib.makeBinPath [pkgs.python313Packages.boto3]}
        '';

        meta.mainProgram = "jumper";
      };
    });
    devShells = nixpkgs.lib.genAttrs systems (
      system: let
        pkgs = import nixpkgs {inherit system;};
      in {
        default = pkgs.mkShell {
          packages = with pkgs; [
            python313
            python313Packages.boto3
            python313Packages.boto3-stubs
            python313Packages.mypy-boto3-iam
            python313Packages.mypy-boto3-sts
          ];
        };
      }
    );
  };
}
