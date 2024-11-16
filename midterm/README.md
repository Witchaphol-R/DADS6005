### Source 1: PageView (stream datagen) (topic1_PageView)

`session_id`: Unique identifier for user session.  
`user_id`: Identifier for the user who triggered the view event.  
`source`: The origin of the view event. (Homepage, Inbox, External)  
`event_timestamp`: The timestamp when the view event occurred.  

### Source 2: UserSession (stream datagen) (topic2_UserSession)

`session_id`: Unique identifier for user session.
`user_id`: Unique identifier for each user.  
`user_name`: The name of the user.  
`login_timestamp`: The timestamp when the user last logged in.  
`device`: The device used by the user for the last login.  

### Source 3: Users (relational database) (topic3_Users)

`user_id`: Unique identifier for each user.  
`age`: The age of the user.  
`gender`: The gender of the user.  
`country`: The primary location of the user.  
`subscription`: The subscription tier of the user (Platinum, Gold, Silver, Standard).  