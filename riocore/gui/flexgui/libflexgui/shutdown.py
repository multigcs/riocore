def save_settings(parent):
    parent.settings.setValue("GUI/window_size", parent.size())
    parent.settings.setValue("GUI/window_position", parent.pos())
