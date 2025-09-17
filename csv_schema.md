Schema : 
```
Course,Branch,College Name,College ID
```

Example:
```
LLB,BA&LLB,ALS,103
```

When using this schema for link generation , system follows this URL structure:

https://www.ipuranklist.com/ranklist/{Course}?batch=22&insti={College ID}&sem=0&branch={Branch}
example:
https://www.ipuranklist.com/ranklist/barch?batch=18&insti=260&sem=0&branch=BARCH

the data picked up, will fill out this:

so we need to get that data out efficiently

Before that, we will use chatgpt to fix and amend the data for a uniform form acorss all,the final link formation will be done with simple script

Then the script -> final enrollment number scraping -> go to /student/page ->get asset : image -> update schema
