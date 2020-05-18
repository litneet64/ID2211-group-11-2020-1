## Check for Duplicates / Possible Cycles

- [x] Check that level-0 parent does not get traversed if he appears on replies or retweets anywhere on the chain.
- [x] Check that level-1.5 tweets searched are unique if this user is searched for more than one time as to not traverse the same tweets over and over on level-2. 
- [x] Check that level-2 tweets are not responses to level-0 seed.
- [x] Check file with previous seed nodes as to not traverse them on next run.
- [x] Check massive list with all traversed nodes.
