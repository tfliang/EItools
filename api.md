#api说明:

task:

1.查看任务详情:
```
url: view/task/{:id}/  GET
input: task_id
output:{
    creator: "test test"
    creator_id: "5b9f0c86530c7094840060a6"
    file_name: "1540722328.000000-16人.csv"
    has_finished: 17
    id: "5bd58e9b8d431508e304d60a"
    publish_time: "2018-10-28 18:25"
    status: 0
    task_name: "重新测试16个"
    total: 16
}
```
2.上传抓取文件
```
url:upload/crawlfile/ POST
input: file:file
output:{
    'file_name':'1000人.csv'
}
```
3.保存task
```
url:save/task/ POST
input:{
    'file_name':"1000人.csv",
    'task_name':"测试1000人"，
    ‘creator_id’:"fdsf12fs3lk4kdo"，
    'creaotr':"张三"
}
output:{
    'info':"upload success"/"upload data error"
    'task_id':"fdsf12fs3lk4kdo"
}
```
4.查看任务列表
```
url: show/tasks/(.+)/(.+)/  GET
input: offset size
output:{
     'total':mongo_client.get_task_count(),
        'offset':offset,
        'size':size,
        'tasks':tasks
}
```
5.下载任务列表
```
url: download/crawldata/(.+)/  GET
input: task_id
output:{
    "message":"task error"
}
```
person:

6.查看抓取完成的人的列表
```
url: view/crawldetail/(.+)/(.+)/(.+)/ GET
input:task_id offset size
output:{
    'total': 123,
    'offset': 0,
    'size': 20,
    'info': total_persons
}
```
7.查看抓取人的信息
````
url: view/persondetail/(.+)/ GET
input:person_id
output:{

}
````
8.更新人的信息
```
url:update/persondetail/ POST
input:{
    'id':"fds89fwer12fdlj34o",
    'name':""

}
```
9.搜索人的信息
```
url:search/person/ POST
input:{
    'search_value':"",
    'task_id':"",
    'offset':"",
    "size":""
}
output:{
    'total': mongo_client.search_crawled_person_num_by_taskId(task_id,person_name),
    'offset': offset,
    'size': size,
    'info': total_persons
}
```
10.查看所有人的变更信息
```
url:/view/person/changeinfolist/0/10/ GET
output:{
    "total": 0,
    "offset": "0",
    "size": "10",
    "info": [
        {
            "name": "王炜",
            "task_id": "5bcea3b38d43152bf8876575",
            "change_info": [
                {
                    "key": "email",
                    "old": "kf@people.cn",
                    "new": "wangwei@nju.edu.cn"
                },
                {
                    "key": "title",
                    "old": "副主任",
                    "new": "主任"
                },
                {
                    "key": "position",
                    "old": "教授,主任",
                    "new": "教授,科长"
                }
            ],
            "id": "5bcea3b58d4315560edced35",
            "task_name": "换用主页模式"
        }
    ]
}
```
11.查看单个人变化的信息

```
url:view/person/changeinfo/5bcea3b58d4315560edced35/
input:person_id
output:
   [
    {
        "name": "王炜",
        "task_id": "5bcea3b38d43152bf8876575",
        "change_info": [
            {
                "key": "email",
                "old": "kf@people.cn",
                "new": "wangwei@nju.edu.cn"
            },
            {
                "key": "title",
                "old": "副主任",
                "new": "主任"
            },
            {
                "key": "position",
                "old": "教授,主任",
                "new": "教授,科长"
            }
        ],
        "id": "5bcea3b58d4315560edced35",
        "task_name": "换用主页模式"
    }
]
```
12.搜索变化的信息

```
url:search/person/changeinfo/ POST
input:
input:{
    'search_value':"",
    'offset':"",
    "size":""
}
output:
   [
    {
        "name": "王炜",
        "task_id": "5bcea3b38d43152bf8876575",
        "change_info": [
            {
                "key": "email",
                "old": "kf@people.cn",
                "new": "wangwei@nju.edu.cn"
            },
            {
                "key": "title",
                "old": "副主任",
                "new": "主任"
            },
            {
                "key": "position",
                "old": "教授,主任",
                "new": "教授,科长"
            }
        ],
        "id": "5bcea3b58d4315560edced35",
        "task_name": "换用主页模式"
    }
]
```
