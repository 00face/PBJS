import bpy
import os

walk_mode_entered = False

def enter_walk_mode():
    """
    Enters Walk Mode in the active 3D Viewport if found.
    """
    global walk_mode_entered
    if not walk_mode_entered:
        # Find the active 3D Viewport area
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                # Create a dictionary with necessary context overrides
                context_override = {
                    "area": area,
                    "space_data": area.spaces.active,
                    "region": area.regions[-1]
                }
                # Enter Walk Mode
                with bpy.context.temp_override(**context_override):
                    bpy.ops.view3d.walk('INVOKE_DEFAULT')
                    walk_mode_entered = True
                    # Check if gamemode.py exists
                    if os.path.isfile("gamemode.py"):
                        try:
                            # Execute gamemode.py
                            bpy.ops.script.python_file_run(filepath="gamemode.py")
                        except Exception as e:
                            print("Failed to execute gamemode.py:", e)
                return

def toggle_fullscreen_and_walk():
    """
    Toggle fullscreen mode and enable Walk Navigation in the 3D Viewport.
    """
    try:
        bpy.ops.screen.screen_full_area()
        # Set the viewport navigation mode to WALK
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.viewport_navigation = 'WALK'
    except Exception as e:
        print("Woops. Error toggling fullscreen and enabling Walk Navigation:", e)

def check_3d_viewport(fullscreen: bool):
    """
    Check if there is a 3D Viewport open and optionally toggle it to fullscreen.

    :param fullscreen: If True, toggles the 3D Viewport to fullscreen.
    """
    viewport_exists = False
    for window in bpy.context.window_manager.windows:
        screen = window.screen
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                viewport_exists = True
                print("3D Viewport is open")
                if fullscreen:
                    try:
                        with bpy.context.temp_override(area=area): # makes area fullscreen
                            bpy.ops.screen.screen_full_area()
                    except Exception as e:
                        print("Woops. Error toggling fullscreen:", e)
    if not viewport_exists:
        # If no 3D Viewport exists, create one
        bpy.ops.screen.area_split(direction='HORIZONTAL')
        area = bpy.context.area
        if area.type == 'VIEW_3D':
            area.spaces[0].show_only_render = True
            area.spaces[0].viewport_shade = 'SOLID'
            if fullscreen:
                # Use a timer to ensure that walk navigation is executed after the viewport is maximized
                bpy.app.timers.register(lambda: toggle_fullscreen_and_walk(), first_interval=0.1)
        else:
            area.type = 'VIEW_3D'
            if fullscreen:
                # Use a timer to ensure that walk navigation is executed after the viewport is maximized
                bpy.app.timers.register(lambda: toggle_fullscreen_and_walk(), first_interval=0.1)

# Define handler function to execute when area type becomes VIEW_3D
def on_area_change_handler(dummy):
    if bpy.context.area is not None and bpy.context.area.type == 'VIEW_3D':
        enter_walk_mode()

# Register the area change handler
bpy.app.handlers.depsgraph_update_post.append(on_area_change_handler)

# Check and optionally toggle the 3D viewport to fullscreen
check_3d_viewport(True)
