# Helper scripts

## Reprocessing script
### Description
This is used if the EQ data for a submission was correct, but for some reason the transformed data wasn't correct. 
This script takes all the tx_ids that need reprocessing and puts them into the queue that downstream looks at.  Luckily, all that's needed is the tx_id
as downstream gets the data needed from sdx-store.

### Usage
 - Add all the tx_ids that need reprocessing to the tx_ids file.  This should have 1 tx_id per line.
 - Run the script with ```python3 reprocess.py```