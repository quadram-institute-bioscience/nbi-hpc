#!/usr/bin/env python3
"""
HPC Home Directory Configuration Script

Configures the home directory of HPC users with necessary settings for NBI/QIB HPC.
"""

import argparse
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Tuple, Optional


class ConfigStatus:
    """Emoji constants for status messages."""
    DONE = "✅"
    SKIPPED = "⏭️ "
    FAILED = "❌"
    INFO = "ℹ️ "


class HPCConfigurator:
    """Main class for HPC configuration."""

    def __init__(self, dry_run: bool = False, force: bool = False, verbose: bool = False):
        self.dry_run = dry_run
        self.force = force
        self.verbose = verbose
        self.bashrc_path = Path.home() / ".bashrc"

    def log(self, message: str, verbose_only: bool = False):
        """Print a message, optionally only in verbose mode."""
        if not verbose_only or self.verbose:
            print(message)

    def check_section_exists(self, start_marker: str, end_marker: str) -> Tuple[bool, Optional[Tuple[int, int]]]:
        """
        Check if a section exists in .bashrc.

        Returns:
            Tuple of (exists, (start_line, end_line)) where line numbers are 0-indexed
        """
        if not self.bashrc_path.exists():
            return False, None

        with open(self.bashrc_path, 'r') as f:
            lines = f.readlines()

        start_idx = None
        end_idx = None

        for i, line in enumerate(lines):
            if start_marker in line:
                start_idx = i
            elif end_marker in line and start_idx is not None:
                end_idx = i
                break

        if start_idx is not None and end_idx is not None:
            return True, (start_idx, end_idx)

        return False, None

    def update_bashrc_section(self, start_marker: str, end_marker: str, content: str, description: str) -> bool:
        """
        Add or update a section in .bashrc.

        Returns:
            True if changes were made, False if skipped
        """
        exists, position = self.check_section_exists(start_marker, end_marker)

        # Ensure .bashrc exists
        if not self.bashrc_path.exists():
            if self.dry_run:
                self.log(f"{ConfigStatus.INFO}Would create {self.bashrc_path}")
            else:
                self.bashrc_path.touch()
                self.log(f"{ConfigStatus.INFO}Created {self.bashrc_path}", verbose_only=True)

        with open(self.bashrc_path, 'r') as f:
            lines = f.readlines()

        section_content = f"{start_marker}\n{content}\n{end_marker}\n"

        if exists and not self.force:
            self.log(f"{ConfigStatus.SKIPPED}{description} (already configured)")
            return False

        if self.dry_run:
            if exists:
                self.log(f"{ConfigStatus.INFO}Would update: {description}")
            else:
                self.log(f"{ConfigStatus.INFO}Would add: {description}")
            self.log(f"  Content:\n{section_content}", verbose_only=True)
            return True

        # Remove existing section if it exists
        if exists:
            start_idx, end_idx = position
            lines = lines[:start_idx] + lines[end_idx + 1:]
            self.log(f"{ConfigStatus.INFO}Removed existing section", verbose_only=True)

        # Add the section at the end
        if lines and not lines[-1].endswith('\n'):
            lines[-1] += '\n'

        # Add a blank line before the section if the file is not empty
        if lines and lines[-1].strip():
            lines.append('\n')

        lines.append(section_content)

        # Write back to file
        with open(self.bashrc_path, 'w') as f:
            f.writelines(lines)

        action = "Updated" if exists else "Added"
        self.log(f"{ConfigStatus.DONE}{action}: {description}")
        return True

    def configure_directory_expansion(self) -> bool:
        """Step 1: Allow directory expansion."""
        start_marker = "#start-shopt: Allow directory expansion"
        end_marker = "#end-shopt"
        content = "shopt -s direxpand"

        return self.update_bashrc_section(
            start_marker, end_marker, content,
            "Directory expansion (shopt -s direxpand)"
        )

    def configure_directory_shortcuts(self) -> bool:
        """Step 2: Add directory shortcuts."""
        start_marker = "#add-locations: Configure shortcuts for some QIB locations"
        end_marker = "#end-locations"
        content = """export SCRATCH=/qib/scratch/users/$USER/
export PACKAGES=/nbi/software/testing/bin/
export OUTGOING=/qib/platforms/Informatics/transfer/outgoing
export INCOMING=/qib/platforms/Informatics/transfer/incoming
export DATABASES=/qib/platforms/Informatics/transfer/outgoing/databases/"""

        return self.update_bashrc_section(
            start_marker, end_marker, content,
            "QIB location shortcuts"
        )

    def configure_nextflow(self) -> bool:
        """Step 3: Configure Nextflow."""
        start_marker = "#add-nf: Configure Nextflow for HPC"
        end_marker = "#end-nf"
        content = """export NXF_ANSI_LOG=false
export NXF_OFFLINE='true'
export NXF_SINGULARITY_CACHEDIR="/qib/platforms/Informatics/transfer/outgoing/singularity/nxf\""""

        return self.update_bashrc_section(
            start_marker, end_marker, content,
            "Nextflow HPC configuration"
        )

    def configure_bioinformatics_packages(self) -> bool:
        """Step 4: Configure Core Bioinformatics packages."""
        start_marker = "#add-lua: Configure Core Bioinformatics packages"
        end_marker = "#end-lua"
        content = "module use /qib/research-projects/bioboxes/lua"

        return self.update_bashrc_section(
            start_marker, end_marker, content,
            "Core Bioinformatics packages"
        )

    def configure_nbi_slurm(self) -> bool:
        """Step 5: Enable the NBI-Slurm utility."""
        start_marker = "#add-nbislurm: Enable the NBI-Slurm utility"
        end_marker = "#end-nbislurm"
        content = "source  /nbi/software/testing/bin/nbi-slurm"

        return self.update_bashrc_section(
            start_marker, end_marker, content,
            "NBI-Slurm utility"
        )

    def install_micromamba(self) -> bool:
        """Step 6: Install micromamba."""
        micromamba_dir = Path.home() / "micromamba"

        # Check if already installed (never overwrite even with --force)
        if micromamba_dir.exists():
            self.log(f"{ConfigStatus.SKIPPED}Micromamba installation (already exists at {micromamba_dir})")
            return False

        if self.dry_run:
            self.log(f"{ConfigStatus.INFO}Would install micromamba to {micromamba_dir}")
            self.log(f"  Steps:", verbose_only=True)
            self.log(f"    1. Download installer from micro.mamba.pm/install.sh", verbose_only=True)
            self.log(f"    2. Run silent installation", verbose_only=True)
            return True

        try:
            # Create temporary directory for installer
            with tempfile.TemporaryDirectory() as tmpdir:
                installer_path = Path(tmpdir) / "install.sh"

                # Download installer
                self.log(f"{ConfigStatus.INFO}Downloading micromamba installer...", verbose_only=True)
                result = subprocess.run(
                    ["curl", "-L", "micro.mamba.pm/install.sh", "-o", str(installer_path)],
                    capture_output=True,
                    text=True
                )

                if result.returncode != 0:
                    self.log(f"{ConfigStatus.FAILED}Micromamba installation (download failed)")
                    self.log(f"  Error: {result.stderr}", verbose_only=True)
                    return False

                # Make installer executable
                installer_path.chmod(0o755)

                # Run installer silently with default values
                self.log(f"{ConfigStatus.INFO}Running micromamba installer...", verbose_only=True)
                result = subprocess.run(
                    [str(installer_path)],
                    stdin=subprocess.DEVNULL,
                    capture_output=True,
                    text=True,
                    cwd=tmpdir
                )

                if result.returncode != 0:
                    self.log(f"{ConfigStatus.FAILED}Micromamba installation (installer failed)")
                    self.log(f"  Error: {result.stderr}", verbose_only=True)
                    return False

            self.log(f"{ConfigStatus.DONE}Installed micromamba to {micromamba_dir}")
            return True

        except Exception as e:
            self.log(f"{ConfigStatus.FAILED}Micromamba installation (exception: {e})")
            return False

    def run_all_configurations(self):
        """Run all configuration steps."""
        self.log("=" * 60)
        self.log("HPC Home Directory Configuration")
        self.log("=" * 60)

        if self.dry_run:
            self.log(f"\n{ConfigStatus.INFO}DRY RUN MODE - No changes will be made\n")

        if self.force:
            self.log(f"{ConfigStatus.INFO}FORCE MODE - Will update all existing sections\n")

        # Run all configuration steps
        self.configure_directory_expansion()
        self.configure_directory_shortcuts()
        self.configure_nextflow()
        self.configure_bioinformatics_packages()
        self.configure_nbi_slurm()
        self.install_micromamba()

        self.log("\n" + "=" * 60)
        if self.dry_run:
            self.log(f"{ConfigStatus.INFO}Dry run completed. Re-run without -d/--dry-run to apply changes.")
        else:
            self.log(f"{ConfigStatus.DONE}Configuration completed!")
            self.log(f"\n{ConfigStatus.INFO}Run 'source ~/.bashrc' to apply changes to your current shell.")
        self.log("=" * 60)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Configure HPC home directory with necessary settings for NBI/QIB HPC.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Run configuration
  %(prog)s -d                 # Show what would change (dry run)
  %(prog)s -f                 # Force update all sections
  %(prog)s -d --verbose       # Dry run with detailed output
        """
    )

    parser.add_argument(
        "-d", "--dry-run",
        action="store_true",
        help="Show what would change without making any modifications"
    )

    parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="Re-configure all bashrc settings (delete and re-add each section)"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output with detailed information"
    )

    args = parser.parse_args()

    # Create configurator and run
    configurator = HPCConfigurator(
        dry_run=args.dry_run,
        force=args.force,
        verbose=args.verbose
    )

    try:
        configurator.run_all_configurations()
    except KeyboardInterrupt:
        print(f"\n\n{ConfigStatus.INFO}Configuration interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n{ConfigStatus.FAILED}Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
