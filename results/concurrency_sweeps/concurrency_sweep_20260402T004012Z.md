# Universal API Concurrency Sweep 20260402T004012Z

## Model Summary

| Model | Price | Tested | Safest | Fastest Stable | Best Wall (s) | Format OK | Recommendation |
| --- | --- | --- | --- | --- | ---: | --- | --- |
| qwen3.5-plus | 1x | 2, 4, 6, 8, 10 | 2 | 10 | 0.06 | yes | 推荐正式实验 |
| qwen3-coder-plus | 1x | 2, 4, 6, 8, 10 | 2 | 10 | 0.06 | yes | 推荐正式实验 |
| kimi-for-coding | 2x | 2, 4, 6, 8, 10 | 2 | 10 | 4.45 | yes | 推荐正式实验 |
| gpt-5.4-mini | 2x | 2, 4, 6, 8, 10 | 2 | 10 | 20.92 | yes | 推荐正式实验 |
| glm-5 | unknown | 2, 4, 6, 8, 10 | 2 | 10 | 4.94 | yes | 推荐正式实验 |
| MiniMax-M2.7 | 1x | 2 | 2 | 2 | 370.86 | yes | 可用但要保守并发 |
| claude-sonnet-4-6 | 1x | 2 | 2 | 2 | 551.69 | yes | 可用但要保守并发 |
| MiniMax-M2.7-highspeed | 1x | 2 | 2 | 2 | 847.80 | yes | 不建议继续 |
| step-3.5-flash | unknown | 2 | 2 | 2 | 2162.92 | yes | 不建议继续 |

## Detailed Runs

- `MiniMax-M2.7` `c=2` `phase1`: verdict=usable_with_caution, wall=370.86s, success=28/30, errors=2, empty=2, thinking=0, truncation=0, retry_records=13, max_retry=10, avg_latency=6.16
  anomalies={'study2_item_02': 2, 'study2_item_09': 2}
  samples=['London', 'David Beckham', 'Big Ben', 'Ben Nevis', 'Fish and chips']
- `MiniMax-M2.7-highspeed` `c=2` `phase1`: verdict=unstable, wall=847.80s, success=22/30, errors=8, empty=8, thinking=0, truncation=0, retry_records=12, max_retry=10, avg_latency=6.99
  anomalies={'study2_item_02': 2, 'study2_item_03': 2, 'study2_item_04': 2, 'study2_item_05': 2, 'study2_item_06': 2, 'study2_item_07': 2, 'study2_item_09': 2, 'study2_item_12': 2}
  samples=['London', 'David Beckham', '\nBig Ben', 'Ben Nevis', 'Winston Churchill']
- `claude-sonnet-4-6` `c=2` `phase1`: verdict=usable_with_caution, wall=551.69s, success=28/30, errors=2, empty=2, thinking=0, truncation=0, retry_records=2, max_retry=10, avg_latency=23.68
  anomalies={'study2_item_12': 2, 'study2_item_13': 2}
  samples=['London', 'David Beckham', 'Donald Trump', 'house', 'Mount Everest']
- `glm-5` `c=2` `phase1`: verdict=stable, wall=28.00s, success=30/30, errors=0, empty=0, thinking=0, truncation=0, retry_records=0, max_retry=0, avg_latency=1.84
  samples=['David Beckham', 'London', 'Buckingham Palace', 'Winston Churchill', 'Fish and chips']
- `glm-5` `c=4` `phase1`: verdict=stable, wall=16.45s, success=30/30, errors=0, empty=0, thinking=0, truncation=0, retry_records=0, max_retry=0, avg_latency=2.07
  samples=['David Beckham', 'The Shard', 'Winston Churchill', 'London', 'Ben Nevis']
- `glm-5` `c=6` `phase1`: verdict=stable, wall=13.86s, success=30/30, errors=0, empty=0, thinking=0, truncation=0, retry_records=0, max_retry=0, avg_latency=2.64
  samples=['David Beckham', 'Winston Churchill', 'Big Ben', 'Snowdon', 'London']
- `glm-5` `c=8` `phase2`: verdict=stable, wall=5.78s, success=30/30, errors=0, empty=0, thinking=0, truncation=0, retry_records=0, max_retry=0, avg_latency=1.41
  samples=['Big Ben', 'Big Ben', 'London', 'Snowdon', 'David Beckham']
- `glm-5` `c=10` `phase2`: verdict=stable, wall=4.94s, success=30/30, errors=0, empty=0, thinking=0, truncation=0, retry_records=0, max_retry=0, avg_latency=1.44
  samples=['Boris Johnson', 'Big Ben', '1984', 'BBC', 'David Beckham']
- `gpt-5.4-mini` `c=2` `phase1`: verdict=stable, wall=158.80s, success=30/30, errors=0, empty=0, thinking=0, truncation=0, retry_records=0, max_retry=0, avg_latency=10.37
  samples=['London', 'David Beckham', 'House', 'Donald Trump', 'Mount Everest']
- `gpt-5.4-mini` `c=4` `phase1`: verdict=stable, wall=82.42s, success=30/30, errors=0, empty=0, thinking=0, truncation=0, retry_records=0, max_retry=0, avg_latency=10.36
  samples=['house', 'David Beckham', 'London', 'Donald Trump', 'Mount Everest']
- `gpt-5.4-mini` `c=6` `phase1`: verdict=stable, wall=73.59s, success=30/30, errors=0, empty=0, thinking=0, truncation=0, retry_records=0, max_retry=0, avg_latency=13.44
  samples=['Fish and chips', 'London', 'Mount Everest', 'David Beckham', 'House']
- `gpt-5.4-mini` `c=8` `phase2`: verdict=stable, wall=23.80s, success=30/30, errors=0, empty=0, thinking=0, truncation=0, retry_records=0, max_retry=0, avg_latency=5.66
  samples=['Mount Everest', 'Ed Sheeran', 'London', 'Big Ben', 'Donald Trump']
- `gpt-5.4-mini` `c=10` `phase2`: verdict=stable, wall=20.92s, success=30/30, errors=0, empty=0, thinking=0, truncation=0, retry_records=0, max_retry=0, avg_latency=6.13
  samples=['David Beckham', 'Harry Potter', 'Donald Trump', 'Mount Everest', 'BBC']
- `kimi-for-coding` `c=2` `phase1`: verdict=stable, wall=17.27s, success=30/30, errors=0, empty=0, thinking=0, truncation=0, retry_records=0, max_retry=0, avg_latency=1.14
  samples=['David Beckham', 'London', 'Buckingham Palace', 'Winston Churchill', 'Ben Nevis']
- `kimi-for-coding` `c=4` `phase1`: verdict=stable, wall=8.78s, success=30/30, errors=0, empty=0, thinking=0, truncation=0, retry_records=0, max_retry=0, avg_latency=1.1
  samples=['Winston Churchill', 'London', 'Buckingham Palace', 'David Beckham', 'Fish and chips']
- `kimi-for-coding` `c=6` `phase1`: verdict=stable, wall=8.19s, success=30/30, errors=0, empty=0, thinking=0, truncation=0, retry_records=0, max_retry=0, avg_latency=1.55
  samples=['Winston Churchill', 'Fish and chips', 'London', 'David Beckham', 'Buckingham Palace']
- `kimi-for-coding` `c=8` `phase2`: verdict=stable, wall=5.25s, success=30/30, errors=0, empty=0, thinking=0, truncation=0, retry_records=0, max_retry=0, avg_latency=1.29
  samples=['Ben Nevis', 'Ed Sheeran', 'Big Ben', 'Winston Churchill', 'David Beckham']
- `kimi-for-coding` `c=10` `phase2`: verdict=stable, wall=4.45s, success=30/30, errors=0, empty=0, thinking=0, truncation=0, retry_records=0, max_retry=0, avg_latency=1.41
  samples=['David Beckham', 'The Shard', 'London', 'Harry Potter', 'Big Ben']
- `qwen3-coder-plus` `c=2` `phase1`: verdict=stable, wall=27.39s, success=30/30, errors=0, empty=0, thinking=0, truncation=0, retry_records=0, max_retry=0, avg_latency=1.81
  samples=['London', 'David Beckham', 'Buckingham Palace', 'Winston Churchill', 'Ben Nevis']
- `qwen3-coder-plus` `c=4` `phase1`: verdict=stable, wall=16.42s, success=30/30, errors=0, empty=0, thinking=0, truncation=0, retry_records=0, max_retry=0, avg_latency=2.1
  samples=['Buckingham Palace', 'London', 'David Beckham', 'Winston Churchill', 'Ben Nevis']
- `qwen3-coder-plus` `c=6` `phase1`: verdict=stable, wall=14.20s, success=30/30, errors=0, empty=0, thinking=0, truncation=0, retry_records=0, max_retry=0, avg_latency=2.67
  samples=['London', 'Big Ben', 'Snowdon', 'Fish and chips', 'David Beckham']
- `qwen3-coder-plus` `c=8` `phase2`: verdict=stable, wall=5.56s, success=30/30, errors=0, empty=0, thinking=0, truncation=0, retry_records=0, max_retry=0, avg_latency=1.35
  samples=['London', 'Snowdon', 'Big Ben', 'Fish and chips', 'David Beckham']
- `qwen3-coder-plus` `c=10` `phase2`: verdict=stable, wall=4.78s, success=30/30, errors=0, empty=0, thinking=0, truncation=0, retry_records=0, max_retry=0, avg_latency=1.5
  samples=['Big Ben', 'Buckingham Palace', '1984', 'London', 'Ben Nevis']
- `qwen3-coder-plus` `c=10` `retest`: verdict=stable, wall=0.06s, success=30/30, errors=0, empty=0, thinking=0, truncation=0, retry_records=0, max_retry=0, avg_latency=1.5
  samples=['London', 'Winston Churchill', 'Ben Nevis', 'Buckingham Palace', 'David Beckham']
- `qwen3.5-plus` `c=2` `phase1`: verdict=stable, wall=29.06s, success=30/30, errors=0, empty=0, thinking=0, truncation=0, retry_records=0, max_retry=0, avg_latency=1.92
  samples=['David Beckham', 'London', 'Winston Churchill', 'Buckingham Palace', 'Ben Nevis']
- `qwen3.5-plus` `c=4` `phase1`: verdict=stable, wall=16.73s, success=30/30, errors=0, empty=0, thinking=0, truncation=0, retry_records=0, max_retry=0, avg_latency=2.11
  samples=['Winston Churchill', 'Buckingham Palace', 'David Beckham', 'London', 'Ben Nevis']
- `qwen3.5-plus` `c=6` `phase1`: verdict=stable, wall=29.84s, success=30/30, errors=0, empty=0, thinking=0, truncation=0, retry_records=0, max_retry=0, avg_latency=3.09
  samples=['Fish and chips', 'London', 'Snowdon', 'David Beckham', 'Buckingham Palace']
- `qwen3.5-plus` `c=8` `phase2`: verdict=stable, wall=23.62s, success=30/30, errors=0, empty=0, thinking=0, truncation=0, retry_records=0, max_retry=0, avg_latency=5.53
  samples=['David Beckham', 'Fish and chips', 'London', 'Ed Sheeran', 'Big Ben']
- `qwen3.5-plus` `c=10` `phase2`: verdict=stable, wall=21.38s, success=30/30, errors=0, empty=0, thinking=0, truncation=0, retry_records=0, max_retry=0, avg_latency=6.52
  samples=['BBC', 'Big Ben', 'London', 'David Beckham', 'Fish and chips']
- `qwen3.5-plus` `c=10` `retest`: verdict=stable, wall=0.06s, success=30/30, errors=0, empty=0, thinking=0, truncation=0, retry_records=0, max_retry=0, avg_latency=6.52
  samples=['Ed Sheeran', 'Big Ben', 'David Beckham', 'Mount Everest', 'Fish and chips']
- `step-3.5-flash` `c=2` `phase1`: verdict=unstable, wall=2162.92s, success=13/30, errors=17, empty=17, thinking=0, truncation=0, retry_records=26, max_retry=10, avg_latency=7.47
  anomalies={'study2_item_02': 4, 'study2_item_03': 4, 'study2_item_04': 4, 'study2_item_07': 4, 'study2_item_11': 2, 'study2_item_12': 2, 'study2_item_13': 4, 'study2_item_05': 2, 'study2_item_06': 2, 'study2_item_08': 2, 'study2_item_14': 2, 'study2_item_15': 2}
  samples=['London', 'Ben Nevis', 'Fish and chips', '1984', 'BBC']
