from datetime import datetime, time, timedelta
from random import randint
from common import *
from config import no_projects_per_line, no_users_per_line
from languages import *
from telegram import InlineKeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, ReplyKeyboardRemove, File, InputFile
import sys

class JiraTask:
    def __init__(self, bot, author, lang, project_list, defaul_project, jira_users, default_priority="Medium"):
        self.bot=bot
        self.lang=lang
        self.jira_users=jira_users
        self.author=author
        self.project=defaul_project
        self.project_list=project_list
        self.priority=default_priority
        self.summary=None
        self.task_to=None
        self.task_text=None
        self.deadline=None
        self.file=[]
        self.task_id=self.author.user_id[:5]+str(datetime.now()).replace(' ','_').replace(':','').replace('.','')[10:]+str(randint(10000,99999))

    def set_priority(self, update, priority):
        self.priority=priority
        self.author.task_priority_set=False
        #keys=InlineKeyboardMarkup([[InlineKeyboardButton(priority, callback_data='priority_change__'+self.task_id+\
        #                            '__'+priority_list[self.lang][priority]) for priority in priority_list[self.lang]]])
        #self.bot.sendMessage(chat_id=update.message.chat_id, text=priority_was_set_message[self.lang].format(\
        #                self.priority), reply_markup=keys)
        keys=ReplyKeyboardMarkup(keyboard=[[comm for comm in task_commands[self.lang].values()],[cancel_key[self.lang],send_task_key[self.lang]]], resize_keyboard=True)
        if self.task_text == None:
            self.bot.sendMessage(chat_id=update.message.chat_id, text=task_create_message[self.lang], reply_markup=keys)
        else:
            self.bot.sendMessage(chat_id=update.message.chat_id, text=task_is_ready_message[self.lang], reply_markup=keys)
    
    def set_project(self, update, project):
        if project in self.project_list:
            self.author.task_project_set=False
            self.project=self.project_list[project]
            project_keys=split_list(self.project_list, no_projects_per_line)
            for i in range(len(project_keys)):
                for j in range(len(project_keys[i])):
                    project_keys[i][j]=InlineKeyboardButton(project_keys[i][j], callback_data='project_change__'+
                                    self.task_id+'__'+self.project_list[project_keys[i][j]])
            #keys=InlineKeyboardMarkup(project_keys)
            #keys=InlineKeyboardMarkup([[InlineKeyboardButton(project, callback_data='project_change__'+
            #                        self.task_id+'__'+self.project_list[project]) for project in self.project_list]])
            #self.bot.sendMessage(chat_id=update.message.chat_id, text=project_was_set_message[self.lang].format(project), reply_markup=keys)
            keys=ReplyKeyboardMarkup(keyboard=[[comm for comm in task_commands[self.lang].values()],[cancel_key[self.lang],send_task_key[self.lang]]], resize_keyboard=True)
            if self.task_text == None:
                self.bot.sendMessage(chat_id=update.message.chat_id, text=task_create_message[self.lang], reply_markup=keys)
            else:
                self.bot.sendMessage(chat_id=update.message.chat_id, text=task_is_ready_message[self.lang], reply_markup=keys)
        else:
            self.author.task_project_set=True
            keys=ReplyKeyboardMarkup(keyboard=[[project for project in self.project_list.values()]], resize_keyboard=True)
            self.bot.sendMessage(chat_id=update.message.chat_id, text=project_error_message[self.lang], reply_markup=keys)
    
    def set_deadline(self, update, deadline):
        if deadline.isnumeric():
            self.deadline=int(deadline)
            self.author.task_deadline_set=False
            keyboard=['1','2','3','4','5','10']
            #keys=InlineKeyboardMarkup([[InlineKeyboardButton(key, callback_data='deadline_change__'+self.task_id+
            #                            '__'+key) for key in keyboard]])
            #self.bot.sendMessage(chat_id=update.message.chat_id, text=deadline_was_set_message[self.lang].format(deadline), reply_markup=keys)
            keys=ReplyKeyboardMarkup(keyboard=[[comm for comm in task_commands[self.lang].values()],[cancel_key[self.lang],send_task_key[self.lang]]], resize_keyboard=True)
            if self.task_text == None:
                self.bot.sendMessage(chat_id=update.message.chat_id, text=task_create_message[self.lang], reply_markup=keys)
            else:
                self.bot.sendMessage(chat_id=update.message.chat_id, text=task_is_ready_message[self.lang], reply_markup=keys)
        else:
            keys=InlineKeyboardMarkup(keyboard=[['1','2','3','4','5','10']],resize_keyboard=True)
            self.author.task_deadline_set=True
            self.bot.sendMessage(chat_id=update.message.chat_id, text=task_deadline_message[self.lang], reply_markup=keys)
    
    def set_summary(self, update, summary):
        self.summary=summary
        self.author.task_summary_set=False
        buttons = self.inline_menu()
        update.message.reply_to_message.edit_text(self.format_summary_message())
        update.message.reply_to_message.edit_reply_markup(reply_markup=buttons)
        #keys=ReplyKeyboardMarkup(keyboard=[[comm for comm in task_commands[self.lang].values()],[cancel_key[self.lang],send_task_key[self.lang]]], resize_keyboard=True)
        #self.bot.sendMessage(chat_id=update.message.chat_id, text=summary_was_set_message[self.lang], reply_markup=keys)
        #if self.task_text is None:
        #    self.bot.sendMessage(chat_id=update.message.chat_id, text=task_create_message[self.lang], reply_markup=keys)
        #else:
        #self.bot.sendMessage(chat_id=update.message.chat_id, text=task_is_ready_message[self.lang], reply_markup=keys)

    def set_description(self, update, description):
        self.task_text=description
        self.author.task_description_set=False
        buttons = self.inline_menu()
        update.message.reply_to_message.edit_text(self.format_summary_message())
        update.message.reply_to_message.edit_reply_markup(reply_markup=buttons)
        #keys=ReplyKeyboardMarkup(keyboard=[[comm for comm in task_commands[self.lang].values()],[cancel_key[self.lang],send_task_key[self.lang]]], resize_keyboard=True)
        #self.bot.sendMessage(chat_id=update.message.chat_id, text=summary_was_set_message[self.lang], reply_markup=keys)
        #if self.task_text is None:
        #    self.bot.sendMessage(chat_id=update.message.chat_id, text=task_create_message[self.lang], reply_markup=keys)
        #else:
        #self.bot.sendMessage(chat_id=update.message.chat_id, text=task_is_ready_message[self.lang], reply_markup=keys)
    
    def set_task_text(self, update, text):
        if self.task_text is None:self.task_text=''
        self.task_text+=text+'\n'
        keys=ReplyKeyboardMarkup(keyboard=[[comm for comm in task_commands[self.lang].values()],[cancel_key[self.lang],send_task_key[self.lang]]], resize_keyboard=True)
        self.bot.sendMessage(chat_id=update.message.chat_id, text=task_is_ready_message[self.lang], reply_markup=keys)
    
    def set_assignee(self, update, assignee):
        self.task_to=assignee
        self.author.task_assignee_set=False
        users_keys=split_list(self.jira_users, no_users_per_line)
        for i in range(len(users_keys)):
            for j in range(len(users_keys[i])):
                users_keys[i][j]=InlineKeyboardButton(users_keys[i][j].decode(), callback_data='user_change__'+self.task_id+\
                                    '__test')#+self.jira_users[users_keys[i][j]])
        keys=InlineKeyboardMarkup(users_keys)
        #keys=InlineKeyboardMarkup([[InlineKeyboardButton(name.decode(), callback_data='user_change__'+self.task_id+\
        #                            '__'+self.jira_users[name]) for name in self.jira_users]])
        #self.bot.sendMessage(chat_id=update.message.chat_id, text=inline_assignee_message[self.lang].format(\
        #                assignee.name), reply_markup=keys)
        keys=ReplyKeyboardMarkup(keyboard=[[comm for comm in task_commands[self.lang].values()],[cancel_key[self.lang],\
                                 send_task_key[self.lang]]], resize_keyboard=True)
        if self.task_text == None:
            self.bot.sendMessage(chat_id=update.message.chat_id, text=task_create_message[self.lang], reply_markup=keys)
        else:
            self.bot.sendMessage(chat_id=update.message.chat_id, text=task_is_ready_message[self.lang], reply_markup=keys)

    def inline_user_change(self, update, user):
        message_id=update.callback_query.message.message_id
        self.task_to=user
        users_keys=split_list(self.jira_users, no_users_per_line)
        for i in range(len(users_keys)):
            for j in range(len(users_keys[i])):
                users_keys[i][j]=InlineKeyboardButton(users_keys[i][j].decode(), callback_data='user_change__'+self.task_id+\
                                    '__'+self.jira_users[users_keys[i][j]])
        keys=InlineKeyboardMarkup(users_keys)
        self.bot.editMessageText(chat_id=update.callback_query.message.chat.id, message_id=message_id, \
            text=inline_assignee_message[self.lang].format(user.name), reply_markup=keys)
        self.bot.answerCallbackQuery(callback_query_id=update.callback_query.id, text=update_is_ok_message[self.lang])

    def inline_user_change_mine(self, update, user):
        query = update.callback_query
        query.answer()
        self.task_to = user
        self.author.task_assignee_set = False
        msg = self.format_summary_message()
        buttons = self.inline_menu()
        query.edit_message_text(text=msg)
        query.edit_message_reply_markup(reply_markup=buttons)

    def inline_priority_change_mine(self, update, priority):
        query = update.callback_query
        query.answer()
        self.priority = priority
        self.author.task_priority_set = False
        msg = self.format_summary_message()
        buttons = self.inline_menu()
        query.edit_message_text(text=msg)
        query.edit_message_reply_markup(reply_markup=buttons)

    def inline_priority_change(self, update, priority):
        message_id=update.callback_query.message.message_id
        self.priority=priority
        for pr in priority_list[self.lang]:
            if priority_list[self.lang][pr]==priority:new_priority=pr
        keys=InlineKeyboardMarkup([[InlineKeyboardButton(priority, callback_data='priority_change__'+self.task_id+\
                                    '__'+priority_list[self.lang][priority]) for priority in priority_list[self.lang]]])
        self.bot.editMessageText(chat_id=update.callback_query.message.chat.id, message_id=message_id, \
                            text=priority_was_set_message[self.lang].format(new_priority), reply_markup=keys)
        self.bot.answerCallbackQuery(callback_query_id=update.callback_query.id, text=update_is_ok_message[self.lang])
        
    def inline_deadline_change(self, update, deadline):
        message_id=update.callback_query.message.message_id
        self.deadline=deadline
        keyboard=['1','2','3','4','5','10']
        keys=InlineKeyboardMarkup([[InlineKeyboardButton(key, callback_data='deadline_change__'+self.task_id+
                                    '__'+key) for key in keyboard]])
        self.bot.editMessageText(chat_id=update.callback_query.message.chat.id, message_id=message_id, \
                        text=deadline_was_set_message[self.lang].format(deadline), reply_markup=keys)
        self.bot.answerCallbackQuery(callback_query_id=update.callback_query.id, text=update_is_ok_message[self.lang])
        
    def inline_project_change(self, update, project):
        message_id=update.callback_query.message.message_id
        self.project=project
        project_keys=split_list(self.project_list, no_projects_per_line)
        for i in range(len(project_keys)):
            for j in range(len(project_keys[i])):
                project_keys[i][j]=InlineKeyboardButton(project_keys[i][j], callback_data='project_change__'+
                                self.task_id+'__'+self.project_list[project_keys[i][j]])
        keys=InlineKeyboardMarkup(project_keys)
        #keys=InlineKeyboardMarkup([[InlineKeyboardButton(project, callback_data='project_change__'+
        #                            self.task_id+'__'+self.project_list[project]) for project in self.project_list]])
        for pr in self.project_list:
            if self.project_list[pr]==project:project=pr
        self.bot.editMessageText(chat_id=update.callback_query.message.chat.id, message_id=message_id, \
                        text=project_was_set_message[self.lang].format(project), reply_markup=keys)
        self.bot.answerCallbackQuery(callback_query_id=update.callback_query.id, text=update_is_ok_message[self.lang])

    def format_summary_message(self, msg=''):
        return('Тема: {0}\n'
               'Описание: {1}\n'
               'Исполнитель: {2}\n'
               'Приоритет: {3}\n\n'
               '{4}').format(self.summary,
                             self.task_text,
                             self.task_to.name if self.task_to is not None else 'None',
                             self.priority,
                             msg)

    def inline_menu(self):
        buttons = [[],[]]
        for key in inline_menu_options:
            button = InlineKeyboardButton(inline_menu_options[key],
                                          callback_data='{0}|kek'.format(key))
            buttons[0].append(button)
        for key in inline_control_options:
            button = InlineKeyboardButton(inline_control_options[key],
                                          callback_data='{0}|kek'.format(key))
            buttons[1].append(button)
        return InlineKeyboardMarkup(buttons)

    def inline_users_menu(self):
        users_buttons = split_list(self.jira_users, no_users_per_line)
        for i in range(len(users_buttons)):
            for j in range(len(users_buttons[i])):
                #print(sys.getsizeof('A|{0}'.format(self.jira_users[users_buttons[i][j]])))
                users_buttons[i][j] = InlineKeyboardButton(users_buttons[i][j].decode(), callback_data='U|{0}'.format(self.jira_users[users_buttons[i][j]]))
                #users_buttons[i][j] = InlineKeyboardButton(users_buttons[i][j].decode(), callback_data='user_change__{0}__{1}'.format(self.task_id, self.jira_users[users_buttons[i][j]]))
        return InlineKeyboardMarkup(users_buttons)