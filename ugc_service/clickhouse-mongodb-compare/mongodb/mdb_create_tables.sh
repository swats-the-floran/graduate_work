docker exec -it mongocfg1 bash -c 'echo "rs.initiate({_id: \"mongors1conf\", configsvr: true, members: [{_id: 0, host: \"mongocfg1\"}, {_id: 1, host: \"mongocfg2\"}, {_id: 2, host: \"mongocfg3\"}]})" | mongosh'  \
    && docker exec -it mongors1n1 bash -c 'echo "rs.initiate({_id: \"mongors1\", members: [{_id: 0, host: \"mongors1n1\"}, {_id: 1, host: \"mongors1n2\"}, {_id: 2, host: \"mongors1n3\"}]})" | mongosh' \
    && sleep 20 \
    && docker exec -it mongos1 bash -c 'echo "sh.addShard(\"mongors1/mongors1n1\")" | mongosh' \
    && echo 'shard1 has been configured' \
    && docker exec -it mongors2n1 bash -c 'echo "rs.initiate({_id: \"mongors2\", members: [{_id: 0, host: \"mongors2n1\"}, {_id: 1, host: \"mongors2n2\"}, {_id: 2, host: \"mongors2n3\"}]})" | mongosh' \
    && docker exec -it mongos1 bash -c 'echo "sh.addShard(\"mongors2/mongors2n1\")" | mongosh' \
    && echo 'shard2 has been configured' \
    && docker exec -it mongors1n1 bash -c 'echo "use movies" | mongosh' \
    && docker exec -it mongos1 bash -c 'echo "sh.enableSharding(\"movies\")" | mongosh' \
    && echo 'db has been created' \
    && docker exec -it mongos1 bash -c 'echo "db.createCollection(\"movies.views\")" | mongosh' \
    && docker exec -it mongos1 bash -c 'echo "sh.shardCollection(\"movies.views\", {\"user_id\": \"hashed\"})" | mongosh' \
    && echo 'views collection has been created' \
    && docker exec -it mongos1 bash -c 'echo "db.createCollection(\"movies.review_ratings\")" | mongosh' \
    && docker exec -it mongos1 bash -c 'echo "sh.shardCollection(\"movies.review_ratings\",{\"review_id\": \"hashed\"})" | mongosh' \
    && echo 'review_ratings collection has been created' \
    && docker exec -it mongos1 bash -c 'echo "db.createCollection(\"movies.film_ratings\")" | mongosh' \
    && docker exec -it mongos1 bash -c 'echo "sh.shardCollection(\"movies.film_ratings\", {\"user_id\": \"hashed\"})" | mongosh' \
    && echo 'film_ratings collection has been created'
    # && docker exec -it mongos1 bash -c 'echo "db.createCollection(\"movies.bookmarks\")" | mongosh' \
    # && docker exec -it mongos1 bash -c 'echo "sh.shardCollection(\"movies.bookmarks\", {\"user_id\": \"hashed\"})" | mongosh' \
    # && echo 'bookmarks collection has been created'
    # && docker exec -it mongos1 bash -c 'echo "db.createCollection(\"movies.reviews\")" | mongosh' \
    # && docker exec -it mongos1 bash -c 'echo "sh.shardCollection(\"movies.reviews\", {\"user_id\": \"hashed\"})" | mongosh' \
    # && echo 'reviews collection has been created' \
