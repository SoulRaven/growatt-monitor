### This document is a reverse engineering of the Iphone ShinePhone application

_Reverse date 03.02.2022 application version is: 5.82_

In the future is possible more that for sure that the API will change, this for my knowledge is the third iteration of not more

**General parameters**
The application user agent header is:

_User-Agent: ShinePhone/5.82 (iPhone; iOS 15.4; Scale/3.00)_


### **Login** - POST

[https://server-api.growatt.com/newTwoLoginAPI.do](https://server-api.growatt.com/newTwoLoginAPI.do)
POST form data contains arguments

| Name              | Value send by app       |
|-------------------|-------------------------|
| appType           | ShinePhone              |
| language          | 1                       |
| loginTime         | 2022-03-02 14:47:48     |
| pad               | iPhone 11 Pro           |
| password **       | < hassed password >     |
| phoneModel        | iPhone 11 Pro           |
| phoneSn           | < phone serial number > |
| phoneType         | ios                     |
| shinephoneVersion | 5.82                    |
| systemVersion     | 15.4                    |
| userName **       | < OSS username >        |

The application call this backend url with different post parameters.
First with _userName_ and _password_ parameters and the second time with all the parameters from the above.

The requirement arguments are username and password.

For some unknown reason the application also send the phone SN. The reason is unknown and somehow GDPR rules

### **GetServerMessages** - GET

[https://server-api.growatt.com/newLoginAPI.do](https://server-api.growatt.com/newLoginAPI.do?op=getServerMessage&accountName=ProGeek ) 

GET query strings

| Name        | Value send by app |
|-------------|-------------------|
| op          | getServerMessage  |
| accountName | < OSS username >  |

Return a JSON object that contains messages from the Growatt backend administrator.
Update notifications, application update, or other thinks. When I document his, the object contains some messages about
a new update and a notification for an Android application,
with the download url: http://cdn-download.com/apk/ShinePhone/ShinePhone.apk

### **getUserMessageNotReadNums** - POST

[https://server-api.growatt.com/newTwoServiceAPI.do](https://server-api.growatt.com/newTwoServiceAPI.do)

This backend api will query for any unread messages that are store in the Growatt OSS account

**QueryString**

| Name | Value send by app         |
|------|---------------------------|
| op   | getUserMessageNotReadNums |

**POST parameters**

| Name        | Value send by app |
|-------------|-------------------|
| accountName | < OSS username >  |
| lan         | 1                 |



