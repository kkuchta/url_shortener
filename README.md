# Lamda-Only Url Shortener

In a massive abuse of AWS Lambda, this project is a fully-functional URL shortener built using only lambda - no data store like redis or dynamodb.

To be clear, this is a Bad Idea®.  There are many better ways to do this.  You should not use this code for stuff.  This is very much a "can it be done?" kinda thing.

A full writeup will be on my site at [kevinkuchta.com](http://kevinkuchta.com) at some point.

# Running

This repo is set up as an [Apex](http://apex.run/) project - use that to deploy and test this.  There's a lot of configuration around API Gateway that's not really covered in this repo that you'd need to get everything working, though.  A live example is or should be up at [kmk.party](https://kmk.party).
