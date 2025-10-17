from pymarc import MARCReader
from marc_converter.logic import marc_to_row

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python test_marc.py <file.mrc>")
        sys.exit(1)
    marc_path = sys.argv[1]
    errors = []
    try:
        with open(marc_path, "rb") as fh:
            reader = MARCReader(fh, to_unicode=True, force_utf8=True, utf8_handling="ignore")
            for idx, rec in enumerate(reader):
                try:
                    row = marc_to_row(rec)
                    print(f"Record {idx+1}:", row)
                except Exception as e:
                    error_msg = f"Error in record {idx+1}: {e}"
                    print(error_msg)
                    errors.append(error_msg)
        if errors:
            print("\nErrors encountered during parsing:")
            for err in errors:
                print(err)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
