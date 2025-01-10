import asyncio
import base64
import io
from typing import Literal

import pyautogui
from PIL import ImageGrab
from anthropic.types.beta import BetaToolComputerUse20241022Param

from .base import BaseAnthropicTool, ToolError, ToolResult

class WindowsComputerTool(BaseAnthropicTool):
    """Windows-specific implementation of the computer tool."""
    
    name: Literal["computer"] = "computer"
    api_type: Literal["computer_20241022"] = "computer_20241022"
    
    def __init__(self):
        super().__init__()
        # Initialize screen size
        self.width, self.height = pyautogui.size()
        pyautogui.FAILSAFE = False  # Disable fail-safe
        
    @property
    def options(self):
        return {
            "display_width_px": self.width,
            "display_height_px": self.height,
            "display_number": None,
        }

    def to_params(self) -> BetaToolComputerUse20241022Param:
        return {
            "name": self.name,
            "type": self.api_type,
            **self.options
        }
        
    async def __call__(self, action: str, coordinate: list[int] | None = None, text: str | None = None, **kwargs):
        if action == "screenshot":
            return await self.take_screenshot()
            
        # For actions that require coordinates
        if action in ["mouse_move", "left_click", "right_click", "double_click"]:
            if not coordinate:
                raise ToolError(f"coordinate is required for {action}")
            if not isinstance(coordinate, (list, tuple)) or len(coordinate) != 2:
                raise ToolError(f"coordinate must be a list or tuple of length 2, got {coordinate}")
            
            x, y = coordinate
            if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
                raise ToolError(f"coordinates must be numbers, got x={x}, y={y}")
            if not (0 <= x <= self.width and 0 <= y <= self.height):
                raise ToolError(f"Coordinates ({x}, {y}) are out of bounds for screen size {self.width}x{self.height}")
            
            try:
                if action == "mouse_move":
                    pyautogui.moveTo(x, y)
                elif action == "left_click":
                    pyautogui.click(x, y)
                elif action == "right_click":
                    pyautogui.rightClick(x, y)
                elif action == "double_click":
                    pyautogui.doubleClick(x, y)
            except Exception as e:
                raise ToolError(f"Failed to perform {action} at coordinates ({x}, {y}): {str(e)}")
            
        # For actions that require text
        elif action in ["type", "key"]:
            if not text:
                raise ToolError(f"text is required for {action}")
            try:
                if action == "type":
                    pyautogui.write(text, interval=0.01)
                elif action == "key":
                    pyautogui.press(text)
            except Exception as e:
                raise ToolError(f"Failed to perform {action} with text '{text}': {str(e)}")
        else:
            raise ToolError(f"Invalid action: {action}")
        
        # Wait briefly for actions to complete
        await asyncio.sleep(0.5)
        return await self.take_screenshot()
        
    async def take_screenshot(self) -> ToolResult:
        """Take a screenshot and return it as base64."""
        screenshot = ImageGrab.grab()
        img_byte_arr = io.BytesIO()
        screenshot.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        return ToolResult(
            base64_image=base64.b64encode(img_byte_arr).decode()
        )
    
