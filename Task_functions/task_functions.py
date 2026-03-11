def get_daily_NASA_img():
    """
    Fetches the daily image from NASA's Astronomy Picture of the Day (APOD) API.

    Returns:
        str: URL of the daily image or an error message.
    """

    api_key = "hmXgra92Mxh6PjwTrObWlHISVXoeTMjg5TwWiLnq"
    url = f"https://api.nasa.gov/planetary/apod?api_key={api_key}"

    try:
        import requests
        response = requests.get(url)
        data = response.json()
        if "url" in data.keys():
            url = data["url"]
        else:
            url = "没有找到图片URL。"
        
        if "explanation" in data.keys():
            explanation = data["explanation"]
            explanation = get_single_ai_response(f"请将以下内容翻译为简体中文，不需要任何解释：{explanation}")
        else:
            explanation = "没有找到图片说明。"

        if url == "没有找到图片URL。":
            return f"{explanation}\n{url}"
        else:
            return f"{explanation}\n@image={url}@"

    except Exception as e:
        return f"Error: {e}"