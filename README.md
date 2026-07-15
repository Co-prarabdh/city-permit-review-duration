# City Permit Review Duration Prediction

This folder contains a complete Project Eris-style synthetic benchmark package.

## Creator Files

- `raw/data.csv` - synthetic source dataset
- `generate_raw_data.py` - reproducible raw data generator
- `prepare.py` - deterministic public/private split creator
- `grade.py` - RMSLE grader
- `config.yaml` - challenge configuration
- `docs/dataset_description.md` - dataset text for the Dataset tab
- `docs/problem_description.md` - problem text for the Problem tab
- `docs/rubrics.md` - initial rubrics
- `docs/submission_notes.md` - title, tags, and creator notes

## Generated Files

- `public/train.csv` - labeled training data for solvers
- `public/test.csv` - unlabeled test data
- `public/sample_submission.csv` - required submission format
- `private/answers.csv` - private ground truth
- `submission.csv` - reference solution output

## Validation Results

- Sample median submission RMSLE: `0.437877`
- Reference solution RMSLE: `0.224967`

Lower is better.
