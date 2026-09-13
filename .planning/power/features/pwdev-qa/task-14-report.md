# Task 14 — implementation report

Status: DONE

## Review fix — round 3

- Closed the remaining Important success-semantics gap. After descriptor-relative publication,
  the currently named destination root is reopened twice with `O_DIRECTORY|O_NOFOLLOW` and
  compared to the retained device/inode identity.
- The published PDF is likewise reopened relative to each freshly named root with
  `O_NOFOLLOW`; regular-file type, device/inode, exact size, and SHA-256 are compared to the
  synchronized temporary PDF. Success therefore requires the nominal destination to contain
  exactly the published PDF during final verification.
- A detected root rename/exchange raises an explicit error and removes the PDF only from the
  retained original inode. A replaced final file is never removed when its inode differs, so
  attacker sentinels and replacement roots remain untouched.
- Root-symlink refusal, descriptor-relative exclusive temp/replace, image revalidation and
  captioning, A4/margins/pagination, and earlier failure cases remain covered. The deferred
  100 × 2000 Minor was not changed.

### Round 3 TDD, adversarial probes, and fresh verification

- RED: root exchange still returned success without a PDF at the nominal destination, and a
  post-publication file exchange also returned success (2 expected failures).
- GREEN: 10 PDF tests passed; full QA regression passed 116 tests.
- Regression proof: stashed only the production fix, observed both new tests fail again,
  restored it, then observed both pass and reran all QA regressions.
- Adversarial probes passed for root symlink, root exchange, post-publication file exchange,
  missing leaf, leaf symlink, SHA-256 mismatch, and MIME mismatch. Root exchange leaves the
  replacement-root sentinel intact and cleans the old-inode PDF; file exchange preserves the
  attacker file while reporting failure.
- Fresh nominal artifact `/tmp/pwdev-qa-f03-14-fix3.YCPmmC/report.pdf`: 54,947 bytes,
  SHA-256 `2157e6a7f5efc9d3ea3ddacbb89e009a1bb228aa1e1fb3b2f53d958d845121fe`, 7 pages,
  one embedded image, and caption extracted intact by pypdf and pdfplumber.
- Pages 1, 6, and 7 rendered with bundled `pdftoppm` were inspected with no clipping,
  overlap, margin, pagination, image, or caption regression. All temporary artifacts and
  generated caches were removed.

## Review fix — round 2

- Addressed the remaining Important root-identity finding. `destination.parent` is now opened
  as a directory with `O_NOFOLLOW`; a root symlink is refused explicitly.
- The opened root's device/inode identity is retained and checked through image revalidation,
  exclusive temporary creation, PDF rendering, cleanup, and final publication.
- The temporary PDF is created with `O_CREAT|O_EXCL|O_NOFOLLOW` relative to the retained root
  descriptor. Final `os.replace` and failure cleanup are also descriptor-relative, so a renamed
  or replaced pathname cannot redirect publication to a different directory.
- Existing leaf-symlink, size, SHA-256, MIME, full-decode, image/legend, A4, margin, and
  pagination behavior remains covered. The deferred 100 × 2000 Minor was not changed.

### Round 2 TDD and fresh verification

- RED: root-symlink export returned success and the root-exchange probe overwrote an
  attacker-controlled sentinel (2 expected failures).
- GREEN: 9 PDF tests passed; full QA regression passed 115 tests.
- Regression proof: stashed only the production fix, observed both root tests fail again,
  restored it, then observed both pass and reran the complete QA regression.
- Root-exchange test renames the validated root after image revalidation and installs a new
  directory plus sentinel at the nominal path. The sentinel remains byte-for-byte unchanged,
  while the PDF is published under the retained original directory inode.
- Fresh artifact `/tmp/pwdev-qa-f03-14-fix2.blxGBd/report.pdf` rendered to 7 PNG pages with
  bundled `pdftoppm`. Pages 1, 6, and 7 were inspected with no clipping, overlap, or layout
  regression; pypdf counted 1 image and both pypdf/pdfplumber extracted its caption intact.
- The PDF, PNG pages, staged fixture, temporary directory, and generated caches were removed.

## Review fix — round 1

- Addressed the Important finding by embedding verified PNG/JPEG evidence with a safe text
  caption containing its evidence ID and staged relative path.
- Image bytes are reopened only beneath `destination.parent` through descriptor-relative
  traversal with `O_NOFOLLOW`; no original or external evidence path is consulted.
- Before a ReportLab flowable is created, the renderer revalidates approval flags, regular-file
  type, exact byte size, SHA-256, declared-versus-detected MIME, and complete image decoding.
  Missing files, symlinks, hash mismatches, MIME mismatches, and malformed images fail explicitly.
- Pending evidence remains absent from both approved references and embedded PDF objects.
- The deferred Minor concerning the final partial token in the 100 × 2000 fixture was not changed.

### Fix TDD and fresh verification

- RED: verified-image test found 0 embedded images; missing/hash/MIME/symlink scenarios raised
  no error (5 expected failures).
- GREEN: 7 PDF tests passed; full QA regression passed 113 tests.
- Regression proof: stashed only the production fix, observed the same 5 failures again, restored
  it, then observed both regression tests pass.
- Fresh visual artifact: `/tmp/pwdev-qa-f03-14-fix1.w4tXnz/report.pdf`, rendered to 7 PNG pages
  at 110 DPI using bundled `pdftoppm`. Pages 5–7 were inspected around the evidence boundary;
  image, caption, margins, pagination, and surrounding sections had no clipping or overlap.
- `pdfimages` and pypdf found exactly 1 embedded 480 × 240 RGB image on page 6. Both pypdf and
  pdfplumber extracted `Evidence image: ev-1 — artifacts/capture.png` intact.
- The fresh PDF, rendered pages, staged fixture, temporary directory, and caches were removed.

## Delivered

- Added `render_pdf(report, destination) -> None` using exactly ReportLab 4.4.9.
- Added A4 output with exact 18 mm document margins, embedded Vera TTF fonts for
  Portuguese accents, repeating headers/footers, `Page X of Y`, textual status labels,
  a page-numbered contents section, status legend, and breakable content blocks.
- Rendered every allowlisted public report field without recalculating criterion results or
  verdicts. ReportLab paragraph markup is escaped, stored commands remain inert, and only
  verified evidence IDs are shown as approved references.
- Writes through a sibling temporary file and atomically replaces the destination only after
  a successful build. Missing or non-4.4.9 ReportLab raises an explicit runtime error.
- Pinned export and verification dependencies in `requirements.txt`; no package was installed.

## TDD and verification

- RED: bundled Python 3.12, `python3 -m unittest tests.test_qa_pdf` — 4 expected
  failures because `qa_pdf.py` was absent.
- Additional RED: blocked-evidence reference test failed because the initial renderer listed
  `ev-pending` as approved; fixed by intersecting references with `verified_evidence`.
- GREEN: bundled Python 3.12, `python3 -m unittest tests.test_qa_pdf` — 5 tests passed.
- Regression: bundled Python 3.12,
  `python3 -m unittest discover -s tests -p 'test_qa_*.py'` — 111 tests passed.
- Load fixture: 100 criteria × 2000 characters produced more than 20 pages; pypdf 6.10.0
  and pdfplumber 0.11.9 each extracted the complete expected token inventory.
- `git diff --check` passed.

## Visual evidence and cleanup

- Generated `/tmp/pwdev-qa-f03-14.ONzNSu/report.pdf` and pages
  `/tmp/pwdev-qa-f03-14.ONzNSu/page-1.png` through `page-7.png` with bundled
  `native/poppler/bin/pdftoppm` at 110 DPI.
- Inspected all 7 pages: margins, headings, page breaks, contents, accents, headers, footers,
  status boxes, and long hashes were readable with no clipping or overlap.
- Removed the PDF, rendered pages, temporary directory, and generated `__pycache__` trees.

## Limitations

- The embedded ReportLab Vera font covers the required Latin Unicode/accented text; scripts
  outside that font's glyph repertoire are not promised by the v1 contract.
