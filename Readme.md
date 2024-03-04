# Cron Expression Parser

A cron expression `* * * * * <command>` is divided into 6 segments.
First 5 segments in particular order are the information required to schedule a job.
Last 6th segment is the actual command.

```
# ┌───────────── minute (0–59)
# │ ┌───────────── hour (0–23)
# │ │ ┌───────────── day of the month (1–31)
# │ │ │ ┌───────────── month (1–12)
# │ │ │ │ ┌───────────── day of the week (0–6) (Sunday to Saturday;
# │ │ │ │ │                                   7 is Sunday on some systems)
# │ │ │ │ │
# │ │ │ │ │
# * * * * * <command>
```

The `command` has to be executed at a particular time in a year.

**Each segment have pre-defined range of applicable values**

There are 5 ways to provides list of applicable values on each segment.

### 1. Select All Values `[*]`

if * is provided it means select full range for that segment

For Example:
`*` on minute segment means select all values in range `0-59`

### 2. Select Single Value `[1]`

if only single integer is provided
then it means select only that particular value from the segment range

For Example:
`1` on minute segment means select only `1` from range `0-59`

### 3. Select List of Values `[1,7,13]`

if integers are provided separated by comma(,)
then it means select only provided list of integers

For Example:
`1,7,13` on minute segment means select only `1`, `7` and `13` only from range `0-59`

### 4. Select Range of Values `10-30`

if integers are provided separated by dash/hyphen(-) then it means
then select range of integers including both integers
*Assumption: first integer is less than second integer*

For Example:
`10-30` on minute segment means select all integers from  `10` to `30` from range `0-59`

### 5. Select List of Ranges `10-15,20-25`

if integers are provided separated by dash/hyphen(-) and comma(,)
then it means first split by comma
and then apply range of values

For Example:
`10-15,20-25` on minute segment means select [10,11,12,13,14,15, 20,21,22,23,24,25] from range `0-59`

## Step modifier

After listing all applicable integers slash(/) modifier will be applied, if provided

For example:
Let's say at hour segment the string is
0-23/2

This means

1. list all integers in range from 0 to 23 --> [0, 1, 2, ..., 22, 23]
2. from this list select value i such that i % 2 == 0

# Execution:

## Install Dependencies:

```
cd CronTabExpressionParser/
python3 -m venv .venv
pip install -r requirements.txt
```

## Execute Parser Command Line:

```
source .venv/bin/activate
python -m parser <cron-job-expression>
```

For Example:

`python -m parser "*/15 0 1,15 * 1-5 /usr/bin/find"
`

```
minute        0 15 30 45
hour          0
day of month  1 15
month         1 2 3 4 5 6 7 8 9 10 11 12
day of week   1 2 3 4 5
command       /usr/bin/find
```


# To Execute Test Cases

```
python -m coverage run -m  pytest tests
python -m coverage html
```
This will generate `htlmlcov/index.html`. Open `index.html` in a browser

```
Module	statements	missing	excluded	coverage
parser/__init__.py	2	0	0	100%
parser/config.py	8	0	0	100%
parser/exceptions.py	2	0	0	100%
parser/models.py	102	2	0	98%
parser/transformers.py	73	6	0	92%
tests/test_parser.py	52	0	0	100%
Total	239	8	0	97%
```