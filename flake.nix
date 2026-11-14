{
  description = "Oxygen GTK theme (GTK 2/3/4), derived from Breeze GTK";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs =
    { self, nixpkgs }:
    let
      systems = [
        "x86_64-linux"
        "aarch64-linux"
      ];
      forAllSystems = f: nixpkgs.lib.genAttrs systems (system: f nixpkgs.legacyPackages.${system});
    in
    {
      packages = forAllSystems (pkgs: rec {
        oxygen-gtk-theme = pkgs.callPackage ./package.nix { };
        default = oxygen-gtk-theme;
      });

      overlays.default = final: _prev: {
        oxygen-gtk-theme = final.callPackage ./package.nix { };
      };
    };
}
