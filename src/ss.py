import dearpygui.dearpygui as dpg

dpg.create_context()

with dpg.window(label="Tutorial", width=400, height=400):
    # create plot
    text = dpg.add_slider_int(max_value=10, min_value=-10)

    dpg.configure_item(text, min_value=-1000)

    print(dpg.get_item_configuration(text).get("min_value"))

    # dpg.set_value(text, True)

dpg.create_viewport(title='Custom Title', width=800, height=600)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
