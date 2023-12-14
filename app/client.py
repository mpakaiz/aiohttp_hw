import asyncio
import aiohttp


async def main():

    client = aiohttp.ClientSession()
    ## создание нового юзера
    response = await client.post('http://127.0.0.1:8080/user',
                                json={
                                    'name': 'user_2',
                                    "password": 'Ww12345678',
                                    "email": "anonymous2@yandex.ru"
                                }
                                 )
    response = await client.post("http://127.0.0.1:8080/login",
                            json={
                                "name": "user_2",
                                "password": "Ww12345678"
                            },
                            )
    print(response.status)
    print(await response.text())

    json = await response.json()
    headers = {"Authorization": f"{json['token']}"}
    ##  создание нового объявления
    response = await client.post("http://127.0.0.1:8080/advertisement",
                            json={
                                "header": "PRADAm Pomidori",
                                "description": "Vah, kakie vkusnie",
                                "user_id": 1,
                            },
                             headers=headers
                            )
    print(response.status)
    print(await response.text())

    ## удаление объявления
    response = await client.delete("http://127.0.0.1:8080/advertisement/1",
                            json={
                                "user_id": 1,
                                "advt_id": 1,
                            },
                             headers=headers
                            )
    print(response.status)
    print(await response.text())

    await client.close()

asyncio.get_event_loop().run_until_complete(main())
