import logging
import simpleobsws

from Dataclasses import OBSText


class OBSRequest:
    @classmethod
    def check_obs_sources(func):
        """
        Checks if a function that will attempt to interact with an OBS scene,
        source or input and makes sure it's available on the connected instance

        Example:
            >>> @check_obs_sources
            >>> async def switch_scene(
            >>>     self,
            >>>     scene_name: str = None,
            >>> ):
            >>>     # function body here
        """

        async def check_obs_wrapper(self, *args, **kwargs):
            relevant_kwargs = {
                name: value
                for name, value in kwargs.items()
                if any(word in name for word in ("source", "scene", "input"))
            }
            for kwarg_name, kwarg_value in relevant_kwargs.items():
                if "source" in kwarg_name:
                    input_sources = getattr(self, "_input_sources", [])
                    scene_sources = getattr(self, "_scene_sources", [])
                    collection = input_sources + scene_sources
                else:
                    collection_name = f"_{kwarg_name.split('_')[0]}s"
                    collection = getattr(self, collection_name, [])

                if kwarg_value not in collection:
                    logging.debug(f"{self._name} is skipping {kwarg_value}")
                else:
                    logging.debug(f"{self._name} is calling {kwarg_value}")
                    return await func(self, *args, **kwargs)

        return check_obs_wrapper

    @classmethod
    async def _call(
        cls,
        type: str = "Call",
        request: simpleobsws.Request = None,
        *args,
        **kwargs,
    ):
        ret = await cls.ws.call(request)  # Perform the request

        if ret.ok():  # Check if the request succeeded
            logging.debug(f"|{cls._name}| {type} succeeded!")
            logging.debug(f"Response data: {ret.responseData}")
            return ret.responseData
        else:
            logging.warn(f"|{cls._name}| {type} failed!")
            logging.warn(f"Response data: {ret.responseData}")
            return ret.responseData

    @classmethod
    @check_obs_sources
    async def toggle_filter(
        cls,
        source_name: str = None,
        filter_name: str = None,
        filter_enabled: bool = False,
    ):
        request = simpleobsws.Request(
            "SetSourceFilterEnabled",
            {
                "sourceName": f"{source_name}",
                "filterName": f"{filter_name}",
                "filterEnabled": filter_enabled,
            },
        )
        await cls._call(type="Toggle filter", request=request)

    @classmethod
    @check_obs_sources
    async def switch_scene(
        cls,
        scene_name: str = None,
    ):
        request = simpleobsws.Request(
            "SetCurrentProgramScene",
            {
                "sceneName": f"{scene_name}",
            },
        )
        await cls._call(type="Switch scene", request=request)

    @classmethod
    @check_obs_sources
    async def update_text(cls, input_name: str = None, text: str = None):
        request = simpleobsws.Request(
            "SetInputSettings",
            {
                "inputName": f"{input_name}",
                "inputSettings": {
                    "text": f"{text}",
                },
            },
        )
        await cls._call(type="Update text", request=request)

    @classmethod
    @check_obs_sources
    async def get_item_id(
        cls, scene_name: str = None, source_name: str = None
    ):
        request = simpleobsws.Request(
            "GetSceneItemId",
            {"sceneName": f"{scene_name}", "sourceName": f"{source_name}"},
        )
        result = await cls._call(type="Get SceneItem id", request=request)
        return result["sceneItemId"]

    @classmethod
    async def get_scene_items(cls, scene_name: str = None):
        request = simpleobsws.Request(
            "GetSceneItemList",
            {"sceneName": f"{scene_name}"},
        )
        result = await cls._call(type="Get SceneItems", request=request)
        scene_items = []
        for scene_item in result["sceneItems"]:
            if scene_item["isGroup"]:
                group_items = await cls.get_group_items(
                    group_name=scene_item["sourceName"]
                )
                for item in group_items:
                    scene_items.append(item)
            else:
                scene_items.append(scene_item)
        return scene_items

    @classmethod
    async def get_group_items(cls, group_name: str = None):
        request = simpleobsws.Request(
            "GetGroupSceneItemList",
            {"sceneName": f"{group_name}"},
        )
        result = await cls._call(type="Get GroupItems", request=request)
        return result["sceneItems"]

    @classmethod
    @check_obs_sources
    async def update_position(
        cls,
        scene_name: str = None,
        position_x: int = 0,
        position_y: int = 0,
        scene_item_id: int = None,
        scene_group_name: str = None,
    ):
        if scene_group_name:
            scene_name = scene_group_name
        request = simpleobsws.Request(
            "SetSceneItemTransform",
            {
                "sceneName": f"{scene_name}",
                "sceneItemId": scene_item_id,
                "sceneItemTransform": {
                    "positionY": position_y,
                    "positionX": position_x,
                },
            },
        )
        await cls._call(type="Update item position", request=request)

    @classmethod
    @check_obs_sources
    async def update_url(cls, input_name: str = None, url: str = None):
        request = simpleobsws.Request(
            "SetInputSettings",
            {
                "inputName": f"{input_name}",
                "inputSettings": {
                    "url": f"{url}",
                },
            },
        )
        await cls._call(type="Update url", request=request)

    @classmethod
    async def update_text_extended(
        cls, item: OBSText = None, scene_item_id: int = None
    ):
        await cls.update_position(
            scene_name=item.scene,
            position_x=item.position_x,
            position_y=item.position_y,
            scene_item_id=scene_item_id,
            scene_group_name="Credit texts group",
        )
        request = simpleobsws.Request(
            "SetInputSettings",
            {
                "inputName": item.source,
                "inputSettings": {
                    "text": item.text,
                    "extents_cx": item.width,
                    "extents_cy": item.height,
                },
            },
        )
        await cls._call(type="Update text extended", request=request)

    @classmethod
    @check_obs_sources
    async def blank_text(cls, input_name: str = None):
        request = simpleobsws.Request(
            "SetInputSettings",
            {
                "inputName": input_name,
                "inputSettings": {
                    "text": "",
                },
            },
        )
        await cls._call(type=f"Blanking {input_name}", request=request)

    @classmethod
    @check_obs_sources
    async def update_input_source(
        cls, input_name: str = None, input_source: str = None
    ):
        video_path = (
            f"C:/Users/micro/Documents/OBS/video-sources/{input_source}"
        )
        request = simpleobsws.Request(
            "SetInputSettings",
            {
                "inputName": f"{input_name}",
                "inputType": "ffmpeg_source",
                "inputSettings": {
                    "local_file": f"{video_path}",
                },
            },
        )
        await cls._call(
            type=f"Changing {input_name}: {input_source}", request=request
        )
