from pathlib import Path
import subprocess
import sys

# Repo root (from .github/scripts -> repo root)
repo_root = Path(__file__).parent.parent.parent.resolve()

# Python executable used in workflow
python_exe = sys.executable

# Submissions directory
SUBMISSIONS_DIR = repo_root / "submissions"

def decrypt_file(enc_path: Path) -> Path:
    """
    Decrypt an .enc file using decrypt.py and return the path to the decrypted file.
    """
    decrypted_path = enc_path.with_suffix('')  # remove .enc
    print(f"Decrypting {enc_path.name} -> {decrypted_path.name}")
    subprocess.run([python_exe, str(repo_root / "encryption" / "decrypt.py"), str(enc_path)], check=True)
    return decrypted_path

def score_file(csv_path: Path):
    """
    Score a CSV file using score_submission.py with --require-metadata.
    """
    print(f"Scoring {csv_path.name}")
    subprocess.run([
        python_exe,
        str(repo_root / "leaderboard" / "score_submission.py"),
        str(csv_path),
        "--require-metadata"
    ], check=True)

def main():
    # Loop over all team folders
    if not SUBMISSIONS_DIR.exists():
        print(f"Submissions directory not found: {SUBMISSIONS_DIR}")
        return

    for team_dir in SUBMISSIONS_DIR.iterdir():
        if not team_dir.is_dir():
            continue

        print(f"\nProcessing team: {team_dir.name}")

        ideal_enc = team_dir / "ideal.enc"
        perturbed_enc = team_dir / "perturbed.enc"

        if not ideal_enc.exists() or not perturbed_enc.exists():
            print(f"Skipping {team_dir.name}: missing .enc files")
            continue

        try:
            # Decrypt submissions
            ideal_csv = decrypt_file(ideal_enc)
            perturbed_csv = decrypt_file(perturbed_enc)

            # Score submissions
            score_file(ideal_csv)
            score_file(perturbed_csv)

        except subprocess.CalledProcessError as e:
            print(f"Error processing {team_dir.name}: {e}")
            continue

    # Finally, update the leaderboard
    print("\nUpdating leaderboard...")
    subprocess.run([python_exe, str(repo_root / "leaderboard" / "update_leaderboard.py")], check=True)
    print("Processing complete!")

if __name__ == "__main__":
    main()
