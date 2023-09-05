# ECONIndexer_API
Repository used to store and manipulate some __Brazilian Economic Indexers__, such as __IPCA, CDI, SELIC__, etc.

The main purpose of this repository is improving my skills with __Python__ and __Streamlit__. Also, I am starting with __MongoDB__, __FastAPI__ and __Deta Space__.


For now, we have 2 apps available in Streamlit and 1 API deployed in Deta Space:

- [user_app](https://econindexerapi-user.streamlit.app/): used to display a full table related to each Economic Indexer, in order to perform some calculation and analyse some charts
![image](https://github.com/CarlosOliveira1988/ECONIndexer_App/assets/70613924/71260c7b-77a6-4d61-aee1-02b30bf14dfe)

- [admin_app](https://econindexerapi-insert.streamlit.app/): used to register the Economic Indexers values in MongoDB (once a month, usually in the 15th day)
![image](https://user-images.githubusercontent.com/70613924/235555422-c236e782-35a3-4bff-8e8b-94383373c330.png)

- [Swagger docs](https://econindexer_api-1-k4103730.deta.app/docs)

In case you want to interact by code with the API, take a look in this Python example:  
![image](https://github.com/CarlosOliveira1988/ECONIndexer_App/assets/70613924/3cfc1b23-8531-47af-a125-412d154fca57)

The response will be like this:  
![image](https://github.com/CarlosOliveira1988/ECONIndexer_App/assets/70613924/d0845a8d-8f90-4275-8682-633eb29d6899)

