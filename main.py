import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gdk, Gio, GLib
import requests
import threading

class TransferWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set up the window
        self.set_title("GitHub Repo Manager")
        self.set_default_size(600, 500)

        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main_box.set_margin_top(20)
        main_box.set_margin_bottom(20)
        main_box.set_margin_start(20)
        main_box.set_margin_end(20)

        # Create header with title
        header = Gtk.HeaderBar()
        self.set_titlebar(header)

        # Theme switcher
        theme_switch = Gtk.Switch()
        theme_switch.connect('notify::active', self.on_theme_switch)
        theme_button = Gtk.Box()
        theme_button.append(Gtk.Image.new_from_icon_name("weather-clear-night-symbolic"))
        theme_button.append(theme_switch)
        header.pack_end(theme_button)

        # Info button
        info_button = Gtk.Button(label="Info")
        info_button.connect("clicked", self.show_info_modal)
        header.pack_start(info_button)

        # Username input
        username_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        username_label = Gtk.Label(label="GitHub Username")
        username_label.set_halign(Gtk.Align.START)
        self.username_entry = Gtk.Entry()
        username_box.append(username_label)
        username_box.append(self.username_entry)

        # Token input with help button
        token_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        token_label_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        token_label = Gtk.Label(label="Personal Access Token")
        token_label.set_halign(Gtk.Align.START)
        help_button = Gtk.Button()
        help_button.set_icon_name("help-about-symbolic")
        help_button.connect('clicked', self.show_pat_instructions)
        token_label_box.append(token_label)
        token_label_box.append(help_button)

        self.token_entry = Gtk.Entry()
        self.token_entry.set_visibility(False)
        token_box.append(token_label_box)
        token_box.append(self.token_entry)

        # New owner input
        new_owner_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        new_owner_label = Gtk.Label(label="New Owner GitHub Username")
        new_owner_label.set_halign(Gtk.Align.START)
        self.new_owner_entry = Gtk.Entry()
        new_owner_box.append(new_owner_label)
        new_owner_box.append(self.new_owner_entry)

        # Fetch button
        self.fetch_button = Gtk.Button(label="Fetch Repositories")
        self.fetch_button.connect('clicked', self.on_fetch_clicked)

        # Repositories list with Select All checkbox
        repo_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        select_all_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        self.select_all_check = Gtk.CheckButton(label="Select All")
        self.select_all_check.connect('toggled', self.on_select_all_toggled)
        select_all_box.append(self.select_all_check)
        repo_box.append(select_all_box)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_vexpand(True)
        scrolled_window.set_min_content_height(200)

        self.repo_list = Gtk.ListBox()
        self.repo_list.set_selection_mode(Gtk.SelectionMode.MULTIPLE)
        scrolled_window.set_child(self.repo_list)
        repo_box.append(scrolled_window)

        # Action buttons box
        action_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

        # Transfer button
        self.transfer_button = Gtk.Button(label="Transfer Selected Repos")
        self.transfer_button.connect('clicked', self.on_transfer_clicked)

        # Delete button
        self.delete_button = Gtk.Button(label="Delete Selected Repos")
        self.delete_button.add_css_class("destructive-action")
        self.delete_button.connect('clicked', self.on_delete_clicked)

        action_box.append(self.transfer_button)
        action_box.append(self.delete_button)

        # Status label
        self.status_label = Gtk.Label()
        self.status_label.set_wrap(True)

        # Progress bar
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_show_text(True)
        self.progress_bar.set_fraction(0)

        # Add all widgets to the main box
        main_box.append(username_box)
        main_box.append(token_box)
        main_box.append(new_owner_box)
        main_box.append(self.fetch_button)
        main_box.append(repo_box)
        main_box.append(action_box)
        main_box.append(self.status_label)
        main_box.append(self.progress_bar)

        # Set the main container as the window's child
        self.set_child(main_box)

    def show_info_modal(self, button):
        # Create a custom dialog with a title
        dialog = Gtk.Dialog(
            transient_for=self,
            modal=True,
        )
        dialog.set_title("App Information")

        # Create the content area
        content_area = dialog.get_content_area()
        content_area.set_spacing(10)
        content_area.set_margin_top(20)
        content_area.set_margin_bottom(20)
        content_area.set_margin_start(20)
        content_area.set_margin_end(20)

        # Heading label (App Name)
        heading = Gtk.Label(label="GitHub Repo Manager")
        heading.set_markup("<b>App Name:</b> GitHub Repo Manager")
        heading.set_halign(Gtk.Align.START)

        # Detailed info with markup
        info_text = """
        <b>Developer:</b> Linxford Kwabena\n
        <b>Contact:</b> linxford7@gmail.com\n
        <b>Social:</b> @linxford\n
        <b>Version:</b> 1.0.0\n
        <b>Description:</b>
        A tool for managing GitHub repositories,
        allowing users to transfer or delete repositories easily.
        """
        info_label = Gtk.Label()
        info_label.set_markup(info_text)
        info_label.set_wrap(True)
        info_label.set_halign(Gtk.Align.START)

        # Add the heading and info to the content area
        content_area.append(heading)
        content_area.append(info_label)

        # Add an OK button to the dialog
        dialog.add_button("OK", Gtk.ResponseType.OK)

        # Connect to destroy the dialog when the OK button is clicked
        dialog.connect("response", lambda dialog, response: dialog.destroy())
        dialog.present()


    def show_pat_instructions(self, button):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="How to Get a Personal Access Token",
        )

        instructions = """
1. Go to GitHub.com and sign in
2. Click your profile picture → Settings
3. Scroll to "Developer settings" (bottom of left sidebar)
4. Click "Personal access tokens" → "Tokens (classic)"
5. Generate new token (classic)
6. Give it a name and select scopes:
   - For transfers: 'repo' and 'delete_repo'
   - For deletions: 'delete_repo'
7. Click "Generate token"
8. Copy the token immediately (it won't be shown again!)

Note: Keep your token secure and don't share it with others.
"""
        dialog.set_property("secondary-text", instructions)
        dialog.connect("response", lambda dialog, response: dialog.destroy())
        dialog.present()

    def on_select_all_toggled(self, checkbutton):
        is_active = checkbutton.get_active()
        for row in self.repo_list:
            if is_active:
                self.repo_list.select_row(row)
            else:
                self.repo_list.unselect_row(row)

    def on_theme_switch(self, switch, gparam):
        """Handle theme switching between light and dark modes"""
        style_manager = Adw.StyleManager.get_default()
        if switch.get_active():
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_DARK)
        else:
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_LIGHT)

    def on_fetch_clicked(self, button):
        username = self.username_entry.get_text()
        token = self.token_entry.get_text()

        if not username or not token:
            self.status_label.set_text("Please enter both username and token.")
            self.status_label.add_css_class("error")
            return

        def fetch_thread():
            try:
                repos = self.fetch_repos(username, token)
                GLib.idle_add(self.update_repo_list, repos)
            except Exception as e:
                GLib.idle_add(self.show_error, str(e))

        self.fetch_button.set_sensitive(False)
        self.status_label.set_text("Fetching repositories...")
        self.progress_bar.set_fraction(0)
        self.select_all_check.set_active(False)
        threading.Thread(target=fetch_thread, daemon=True).start()

    def on_transfer_clicked(self, button):
        selected_rows = self.repo_list.get_selected_rows()
        new_owner = self.new_owner_entry.get_text()
        token = self.token_entry.get_text()

        if not selected_rows or not new_owner:
            self.status_label.set_text("Please select repositories and provide a new owner.")
            self.status_label.add_css_class("error")
            return

        self.transfer_button.set_sensitive(False)
        self.progress_bar.set_fraction(0)
        self.status_label.set_text("Transferring repositories...")

        def transfer_thread():
            total_repos = len(selected_rows)
            for index, row in enumerate(selected_rows):
                repo_name = row.get_child().get_text()
                try:
                    status = self.transfer_repo(token, repo_name, new_owner)
                    if status == 202:  # GitHub returns 202 Accepted for transfer
                        GLib.idle_add(self.show_success, f"Transfer of '{repo_name}' initiated.")
                    else:
                        GLib.idle_add(self.show_error, f"Failed to transfer '{repo_name}'.")
                except Exception as e:
                    GLib.idle_add(self.show_error, f"Error transferring '{repo_name}': {str(e)}")

                GLib.idle_add(self.update_progress, index + 1, total_repos)

        threading.Thread(target=transfer_thread, daemon=True).start()

    def on_delete_clicked(self, button):
        selected_rows = self.repo_list.get_selected_rows()
        token = self.token_entry.get_text()

        if not selected_rows:
            self.status_label.set_text("Please select repositories to delete.")
            self.status_label.add_css_class("error")
            return

        self.delete_button.set_sensitive(False)
        self.progress_bar.set_fraction(0)
        self.status_label.set_text("Deleting repositories...")

        def delete_thread():
            total_repos = len(selected_rows)
            for index, row in enumerate(selected_rows):
                repo_name = row.get_child().get_text()
                try:
                    status = self.delete_repo(token, repo_name)
                    if status == 204:  # GitHub returns 204 No Content for successful deletion
                        GLib.idle_add(self.show_success, f"'{repo_name}' successfully deleted.")
                    else:
                        GLib.idle_add(self.show_error, f"Failed to delete '{repo_name}'.")
                except Exception as e:
                    GLib.idle_add(self.show_error, f"Error deleting '{repo_name}': {str(e)}")

                GLib.idle_add(self.update_progress, index + 1, total_repos)

        threading.Thread(target=delete_thread, daemon=True).start()

    def fetch_repos(self, username, token):
        """Fetch the repositories from GitHub"""
        url = f"https://api.github.com/users/{username}/repos"
        headers = {'Authorization': f'token {token}'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    def transfer_repo(self, token, repo_name, new_owner):
        """Transfer the repository to a new owner"""
        url = f"https://api.github.com/repos/{repo_name}/transfer"
        headers = {'Authorization': f'token {token}', 'Accept': 'application/vnd.github+json'}
        data = {"new_owner": new_owner}
        response = requests.post(url, headers=headers, json=data)
        return response.status_code

    def delete_repo(self, token, repo_name):
        """Delete the repository from GitHub"""
        url = f"https://api.github.com/repos/{repo_name}"
        headers = {'Authorization': f'token {token}'}
        response = requests.delete(url, headers=headers)
        return response.status_code

    def update_repo_list(self, repos):
        """Update the UI with the fetched repositories"""
        self.repo_list.remove_all()
        for repo in repos:
            row = Gtk.ListBoxRow()
            label = Gtk.Label(label=repo['full_name'])
            row.set_child(label)
            self.repo_list.append(row)
        self.repo_list.show_all()
        self.fetch_button.set_sensitive(True)
        self.status_label.set_text("Repositories fetched.")
        self.status_label.remove_css_class("error")

    def update_progress(self, current, total):
        """Update the progress bar"""
        self.progress_bar.set_fraction(current / total)
        if current == total:
            self.transfer_button.set_sensitive(True)
            self.delete_button.set_sensitive(True)

    def show_error(self, message):
        """Display an error message"""
        self.status_label.set_text(message)
        self.status_label.add_css_class("error")
        self.transfer_button.set_sensitive(True)
        self.delete_button.set_sensitive(True)

    def show_success(self, message):
        """Display a success message"""
        self.status_label.set_text(message)
        self.status_label.remove_css_class("error")

class TransferApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        win = TransferWindow(application=app)
        win.present()

if __name__ == "__main__":
    app = TransferApp(application_id="com.github.repo.manager")
    app.run()
