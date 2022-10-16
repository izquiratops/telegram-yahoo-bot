export $(egrep  -v '^#'  /run/secrets/* | xargs)
