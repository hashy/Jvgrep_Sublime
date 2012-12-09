# -*- coding: utf-8 -*-
import sublime
import sublime_plugin
import subprocess


class JvgrepCommand(sublime_plugin.WindowCommand):
    def __init__(self, view):
        settings = sublime.load_settings('Jvgrep.sublime-settings')
        self.jvgrep_path = settings.get('jvgrep_path', 'jvgrep')
        self.jvgrep_option = settings.get('jvgrep_option', '')
        self.search_path = None
        super(JvgrepCommand, self).__init__(view)

    def cwd_for_window(self, window):
        """
        Return the working directory
        In the common case when the user has one folder open, return that.
        Otherwise, return one of the following (in order of preference):
            1) One of the open folders, preferring a folder containing the active file.
            2) The directory containing the active file.
            3) The user's home directory.
        """
        folders = window.folders()
        if len(folders) == 1:
            return folders[0]
        else:
            active_view = window.active_view()
            active_file_name = active_view.file_name() if active_view else None
            if not active_file_name:
                return folders[0] if len(folders) else os.path.expanduser("~")
            for folder in folders:
                if active_file_name.startswith(folder):
                    return folder
            return os.path.dirname(active_file_name)

    def panel_search_done(self, str):
        jvgrep_path = self.jvgrep_path
        if self.jvgrep_option:
            jvgrep_path += ' ' + self.jvgrep_option
        jvgrep_path += ' ' + str
        if self.search_path:
            for search_path in self.search_path:
                # Windows Path
                jvgrep_path += ' "' + search_path + '"'
        else:
            search_path = self.cwd_for_window(self.window)
            if search_path:
                # Windows Path
                jvgrep_path += ' "' + search_path + '"'
        pipe = subprocess.Popen(jvgrep_path, shell=True, stdout=subprocess.PIPE).stdout
        results = pipe.read()
        pipe.close()
        newv = self.window.new_file()
        newv.set_name('jvgrep result')
        newv.set_syntax_file('Packages/Jvgrep_Sublime/jvgrep Results.tmLanguage')
        newv.set_scratch(True)
        e = newv.begin_edit()
        # print results
        newv.insert(e, 0, results)
        #newv.insert(e, 0, jvgrep_path)
        newv.end_edit(e)

    def run(self):
        self.search_path = None
        defval = self.window.active_view().substr(self.window.active_view().sel()[0])
        self.window.show_input_panel('jvgrep: ', defval, self.panel_search_done, None, None)

    def run(self, **args):
        if args.has_key("dirs"):
            self.search_path = args["dirs"]
        else:
            self.search_path = None
        defval = self.window.active_view().substr(self.window.active_view().sel()[0])
        self.window.show_input_panel('jvgrep: ', defval, self.panel_search_done, None, None)
