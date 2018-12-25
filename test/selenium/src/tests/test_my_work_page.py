# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""My Work page smoke tests."""
# pylint: disable=no-self-use
# pylint: disable=invalid-name
# pylint: disable=too-few-public-methods
# pylint: disable=unused-argument
import re

import pytest  # pylint: disable=import-error

from lib import base, url, users
from lib.constants import objects, element
from lib.page import dashboard, lhn
from lib.page.widget import generic_widget
from lib.utils import selenium_utils


class TestMyWorkPage(base.Test):
  """Tests My Work page, part of smoke tests, section 2."""

  @pytest.mark.smoke_tests
  def test_destructive_horizontal_nav_bar_tabs(self, new_controls_rest,
                                               my_work_dashboard, selenium):
    """Tests that several objects in widget can be deleted sequentially.
    Preconditions:
    - Controls created via REST API.
    """
    controls_tab = my_work_dashboard.select_controls()
    for _ in xrange(controls_tab.member_count):
      counter = controls_tab.get_items_count()
      (controls_tab.select_member_by_num(0).
       three_bbs.select_delete().confirm_delete())
      controls_tab.wait_member_deleted(counter)
    controls_generic_widget = generic_widget.Controls(
        selenium, objects.CONTROLS)
    expected_widget_members = []
    actual_widget_members = controls_generic_widget.members_listed
    assert expected_widget_members == actual_widget_members

  @pytest.mark.smoke_tests
  def test_redirect(self, header_dashboard, selenium):
    """Tests if user is redirected to My Work page after clicking on
    the my work button in user dropdown."""
    header_dashboard.select_my_work()
    expected_url = url.Urls().dashboard + url.Widget.INFO
    actual_url = selenium.current_url
    assert expected_url == actual_url

  @pytest.mark.smoke_tests
  def test_lhn_stays_expanded(self, header_dashboard, selenium):
    """Tests if, after opening LHN, it slides out and stays expanded."""
    lhn_menu = header_dashboard.open_lhn_menu()
    initial_position = lhn_menu.my_objects.element.location
    selenium_utils.wait_until_stops_moving(lhn_menu.my_objects.element)
    selenium_utils.hover_over_element(
        selenium, dashboard.Header(selenium).button_my_tasks.element)
    expected_el_position = initial_position
    actual_el_position = lhn.Menu(selenium).my_objects.element.location
    assert expected_el_position == actual_el_position

  @pytest.mark.smoke_tests
  def test_lhn_remembers_tab_state(self, header_dashboard, selenium):
    """Tests if LHN remembers which tab is selected (my or all objects) after
    closing it."""
    lhn_menu = header_dashboard.open_lhn_menu()
    # check if all objects tab is selected by default
    assert selenium_utils.is_value_in_attr(
        lhn_menu.all_objects.element) is True
    for tab in ['my_objects', 'all_objects']:
      getattr(header_dashboard.open_lhn_menu(), 'select_{0}'.format(tab))()
      header_dashboard.close_lhn_menu()
      selenium.refresh()
      new_lhn_menu = dashboard.Header(selenium).open_lhn_menu()
      # check if selected tab saves state
      assert selenium_utils.is_value_in_attr(
          getattr(new_lhn_menu, tab).element) is True

  @pytest.mark.smoke_tests
  def test_lhn_pin(self, header_dashboard):
    """Tests if pin is present and if it's default state is off."""
    lhn_menu = header_dashboard.open_lhn_menu()
    assert lhn_menu.pin.is_activated is False

  @pytest.mark.smoke_tests
  def test_user_menu_checkbox(self, header_dashboard):
    """Tests user menu checkbox. With that also user menu itself is
    tested since model initializes all elements (and throws and
    exception if they're not present."""
    user_list = header_dashboard.open_user_list()
    user_list.checkbox_daily_digest.click()
    user_list.checkbox_daily_digest.element.get_attribute('disabled')
    # restore previous state
    user_list.checkbox_daily_digest.click()

  @pytest.mark.smoke_tests
  def test_lhn_objects_numbers(self, header_dashboard):
    """Tests LHN menu objects.
    Check LHN contains the list of the objects with number in brackets."""
    lhn_menu = header_dashboard.open_lhn_menu().select_all_objects()
    for item in element.Lhn.BASE_OBJS:
      lhn_item = lhn_menu.toggle(item)
      assert lhn_item.text == \
          item.upper() + ' (' + str(lhn_item.members_count) + ')'
    for item in element.Lhn.SUB_OBJS:
      assert lhn_menu.toggle(item).text == item.replace('_or_', '/').upper()
      lhn_item = lhn_menu.select(item)
      lhn_item.update_members()
      for item_sub in getattr(element.Lhn, item.upper() + '_MEMBERS'):
        lhn_item_sub = lhn_item.toggle(item_sub)
        assert lhn_item_sub.text == \
            item_sub.replace('_', ' ').title() + \
            ' (' + str(lhn_item_sub.members_count) + ')'

  @pytest.mark.smoke_tests
  def test_lhn_objects_expand_collapse(self, header_dashboard):
    """Tests LHN menu objects.
    Check expand/collapse objects"""
    lhn_menu = header_dashboard.open_lhn_menu().select_all_objects()
    for item in element.Lhn.BASE_OBJS:
      assert lhn_menu.is_selectable(item) is True
      lhn_menu.select(item)
    for item in element.Lhn.SUB_OBJS:
      assert lhn_menu.is_selectable(item) is True
      lhn_item = lhn_menu.select(item)
      for item_sub in getattr(element.Lhn, item.upper() + '_MEMBERS'):
        assert lhn_item.is_selectable(item_sub) is True
        lhn_item.select(item_sub)

  @pytest.mark.smoke_tests
  def test_user_menu_buttons(self, header_dashboard):
    """Tests user menu buttons and their icons (styles for icons)
    """
    USER_MENU_BUTTONS = ('logout', 'data_export', 'admin_dashboard', 'help')
    user_menu = header_dashboard.open_user_list()
    for btn_name in USER_MENU_BUTTONS:
      assert user_menu.get_button_icon(btn_name) != ''
    assert getattr(user_menu, 'email').text == users.current_user().name

  @pytest.mark.smoke_tests
  def test_lhn_info_popup(self, header_dashboard, new_program_rest):
    """Tests LHN item info popup
    """
    header_dashboard.button_dashboard.click()
    programs = header_dashboard.\
        open_lhn_menu().\
        select_all_objects().\
        select_programs()
    program_title = programs.members_loaded[0].text
    assert program_title == \
        programs.\
        hover_over_visible_member(program_title).\
        title.text

  @pytest.mark.smoke_tests
  def test_info_panel_close_button(self, my_work_dashboard, new_program_rest):
    """Tests My Work Info panel close button
    """
    my_work_dashboard.button_dashboard.click()
    btn_close = my_work_dashboard.select_programs().\
        tree_view.\
        select_member_by_title(new_program_rest.title).\
        panel.button_close
    assert btn_close.exists is True
    btn_close.js_click()
    btn_close.wait_until_not(lambda e: e.exists)

  @pytest.mark.smoke_tests
  def test_info_panel_minimize_button(self, my_work_dashboard,
                                      new_program_rest):
    """Tests My Work Info panel minimize button
    """
    my_work_dashboard.button_dashboard.click()
    program_info_panel = my_work_dashboard.select_programs().\
        tree_view.\
        select_member_by_title(new_program_rest.title).\
        panel
    btn_minimize = program_info_panel.button_minimize
    assert btn_minimize.exists is True
    btn_minimize.js_click()
    assert program_info_panel.is_minimized is True

  @pytest.mark.smoke_tests
  def test_info_panel_maximize_button(self, my_work_dashboard,
                                      new_program_rest):
    """Tests My Work Info panel maximize button
    """
    my_work_dashboard.button_dashboard.click()
    program_info_panel = my_work_dashboard.select_programs().\
        tree_view.\
        select_member_by_title(new_program_rest.title).\
        panel
    program_info_panel.button_minimize.js_click()
    btn_maximize = program_info_panel.button_maximize
    assert btn_maximize.exists is True
    btn_maximize.js_click()
    assert program_info_panel.is_maximized is True

  @pytest.mark.smoke_tests
  def test_info_panel_content(self, my_work_dashboard, new_program_rest):
    """Tests My Work Info panel content
    """
    my_work_dashboard.button_dashboard.click()
    assert new_program_rest.title == my_work_dashboard.select_programs().\
        tree_view.\
        select_member_by_title(new_program_rest.title).\
        panel.title

  @pytest.mark.smoke_tests
  def test_info_panel_3bbs(self, my_work_dashboard, new_program_rest):
    """Tests My Work Info panel
    """
    my_work_dashboard.button_dashboard.click()
    panel_three_bbs = my_work_dashboard.select_programs().\
        tree_view.\
        select_member_by_title(new_program_rest.title).three_bbs
    assert panel_three_bbs.exists is True

  @pytest.mark.smoke_tests
  def test_navbar_tabs(self, my_work_dashboard):
    """Tests Nav bar on My Work page
    """
    my_work_dashboard.button_dashboard.click()
    my_work_dashboard.wait_to_be_init()
    tabs = my_work_dashboard.get_visible_tabs
    # At least Info tab should be present
    assert tabs
    for tab in tabs:
      # Check name for each tab
      assert re.match(r'Info|(.*) \((\d*)\)', tab.name) is not None
      # Check icon for each tab
      assert tab.tab_icon.exists is True

  @pytest.mark.smoke_tests
  def test_navbar_add_tab(self, my_work_dashboard):
    """Tests Nav bar Add tab doesn't exist on My Work page
    """
    my_work_dashboard.button_dashboard.click()
    my_work_dashboard.wait_to_be_init()
    assert my_work_dashboard.is_add_tab_present is False

  @pytest.mark.smoke_tests
  def test_all_objects(self, my_work_dashboard):
    """Tests number of objects in LHN and in All Objects
    """
    lhn_objects = my_work_dashboard.\
        open_lhn_menu().\
        select_all_objects().\
        get_all_lhn_objects_as_set
    all_objects_objects = \
        set([tab.name for tab in my_work_dashboard.
            select_all_objects().get_visible_tabs])
    if all_objects_objects.issubset(lhn_objects) is False:
      pytest.xfail(
          reason="\nGGRC-2756 Numbers in brackets in LHN are not correspond "
                 "with numbers in tabs on on All objects page:\n" +
                 str(lhn_objects) + "\n" +
                 str(all_objects_objects)
      )
    assert all_objects_objects.issubset(lhn_objects) is True
