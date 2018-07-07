
#broker就是进行任务分发的
broker_url = "redis://127.0.0.1/14"
#result  我们的人物异步执行结束之后有一个结果  保存结果的db
result_backend = "redis://127.0.0.1/15"