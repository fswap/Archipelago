# Fuzzing w/ Regressions

The way this works (for those not familiar with the concept of fuzzing) is
we run the a custom app that basically just runs the world generation a TON of times
and checks for errors. If any of the pre-defined errors (or random exceptions) occur,
then we consider the worldgen to be broken or wrong.

If that happens, we save the worldgen into a file here. We then have a custom regression
test that runs the worldgen against ALL of the errors saved here. 

Until we fix the error, these tests will continue to fail with the same error.

Once we resolve the error, these files stay as regression tests to ensure that specific
issue doens't crop up again.

## Idea behind running the fuzzer

Fuzzers aren't deterministic, so you basically just run them for some number of iterations or length
of time to hopefully run into a random bug.