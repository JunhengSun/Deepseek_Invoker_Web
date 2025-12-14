# Deepseek Invoker Web

* Introduction: This is a website that calls the DeepSeek API, simply encompassing common features of AI websites such as registration, login, creating or selecting sessions, and conversations. It utilizes the Flask framework with a SQLite-driven database. 

* Notably, pop-up messages are implemented through Flask's flash functionality, and all buttons are handled via HTML redirects or form POST submissions (the conversation feature does not use streaming transmission). Viewing session details is achieved through simple JavaScript. 

## URL Overview

* `/`
    * <img src="resources/1.png" style="zoom:20%;" />

* `/register`
    * <img src="resources/2.png" style="zoom:20%;" />

* `/login`
    * <img src="resources/3.png" style="zoom:20%;" />

* `/chat`
    * <img src="resources/5.png" style="zoom:20%;" />

* `/chat/create`
    * <img src="resources/6.png" style="zoom:20%;" />

* `/chat/<int:session_id>`
    * <img src="resources/7.png" style="zoom:20%;" />

* `/chat/history`
    * <img src="resources/8.png" style="zoom:20%;" />
    * After clicking to expand the details: <img src="resources/9.png" style="zoom:20%;" />