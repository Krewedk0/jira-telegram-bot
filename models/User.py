from datetime import datetime, time, timedelta
from models import JiraTask
from random import randint
from languages import *
from common import *
from config import *
from telegram import InlineKeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, ReplyKeyboardRemove, File, InputFile, ParseMode
import logging

class User:
    def __init__(self, user_id, name, default_project, jira_users, project_list, jirauser, username=None, isAssignee=True, language='en', priority='Medium'):
        self.user_id=user_id
        self.name=name
        self.project=default_project
        self.jira_users=jira_users
        self.project_list=project_list
        self.jirauser=jirauser
        self.username=username
        self.isAssignee=isAssignee
        self.language=language
        self.priority=priority
        self.task_assignee_set = False
        self.task_priority_set = False
        self.task_summary_set = False
        self.task_description_set = False
        self.createtask = False

        self.reset()

    def init_task(self, bot, update):
        self.bot=bot
        self.task=JiraTask.JiraTask(defaul_project=self.project, default_priority=self.priority,bot=bot, author=self, lang=self.language, project_list=self.project_list, jira_users=self.jira_users)
        self.createtask=True
        self.task_assignee_set=True

        reply_markup = self.task.inline_users_menu()
        msg = self.task.format_summary_message('Выберите исполнителя')
        update.message.reply_text(msg, reply_markup=reply_markup)

        #users_keys=split_list(self.jira_users, no_users_per_line)
        #for i in range(len(users_keys)):
        #    for j in range(len(users_keys[i])):
        #        users_keys[i][j]=users_keys[i][j].decode()
        #users_keys.append([cancel_key[self.language]])
        #keys=ReplyKeyboardMarkup(keyboard=users_keys, resize_keyboard=True)
        #self.bot.sendMessage(chat_id=update.message.chat_id, text=task_assignee_message[self.language], reply_markup=keys)

    def inline_ask_for_assignee(self, update):
        query = update.callback_query
        query.answer()
        self.task_assignee_set = True
        self.task_summary_set = False
        self.task_description_set = False
        reply_markup = self.task.inline_users_menu()
        msg = self.task.format_summary_message('Выберите исполнителя')
        query.edit_message_text(text=msg)
        query.edit_message_reply_markup(reply_markup=reply_markup)

    def inline_ask_for_priority(self, update):
        query = update.callback_query
        query.answer()
        self.task_priority_set = True
        buttons = [[InlineKeyboardButton(priority, callback_data='P|{0}'.format(priority)) for priority in priority_list[self.language].values()]]
        reply_markup = InlineKeyboardMarkup(buttons)
        msg = self.task.format_summary_message('Выберите приоритет')
        query.edit_message_text(text=msg)
        query.edit_message_reply_markup(reply_markup=reply_markup)

    def inline_ask_for_summary(self, update):
        query = update.callback_query
        query.answer()
        self.task_summary_set = True
        self.task_description_set = False
        msg = self.task.format_summary_message('Напишите название задачи')
        query.edit_message_text(text=msg)

    def inline_ask_for_description(self, update):
        query = update.callback_query
        query.answer()
        self.task_description_set = True
        self.task_summary_set = False
        msg = self.task.format_summary_message('Напишите описание задачи')
        query.edit_message_text(text=msg)
        
    def ask_for_summary(self, update):
        self.task_summary_set=True
        keys=ReplyKeyboardMarkup(keyboard=[[comm for comm in task_commands[self.language].values()],\
                        [cancel_key[self.language],send_task_key[self.language]]], resize_keyboard=True)
        self.bot.sendMessage(chat_id=update.message.chat_id, text=task_summary_message[self.language], reply_markup=keys)
    
    def ask_for_deadline(self, update):
        keys=ReplyKeyboardMarkup(keyboard=[['1','2','3','4','5','10']],resize_keyboard=True)
        self.task_deadline_set=True
        self.bot.sendMessage(chat_id=update.message.chat_id, text=task_deadline_message[self.language], reply_markup=keys)
    
    def ask_for_priority(self, update):
        keys=ReplyKeyboardMarkup(keyboard=[[priority for priority in priority_list[self.language]],[cancel_key[self.language]]],resize_keyboard=True)
        self.task_priority_set=True
        self.bot.sendMessage(chat_id=update.message.chat_id, text=task_priority_message[self.language], reply_markup=keys)
    
    def ask_project(self, update):
        self.task_project_set=True
        project_keys=split_list(self.project_list, no_projects_per_line)
        keys=ReplyKeyboardMarkup(keyboard=project_keys, resize_keyboard=True)
        self.bot.sendMessage(chat_id=update.message.chat_id, text=task_project_message[self.language], reply_markup=keys)

    def create_task(self, update, jira, sprint):
        logging.debug("User.create_task: {0}, {1}, {2}".format(self.task.project, self.task.summary, self.task.task_text))
        if self.task.task_text is None:
            self.task.task_text = ''
        if self.task.task_text is not None and self.task.task_to is not None:
            if self.task.summary is None:
                self.task.summary=self.name+': '+" ".join(self.task.task_text.split()[:5])
            jf={'project':self.task.project,
                'summary':self.task.summary,
                'description':self.task.task_text,
                'issuetype':{'name':'Task'},
                'assignee':{'accountId':self.task.task_to.jirauser},
                'priority':{'name':self.task.priority}
            }
            if sprint != 0:
                jf['customfield_10020'] = sprint
            if self.task.deadline is not None:
                jf['duedate']=str((datetime.now()+timedelta(days=int(self.task.deadline))).date())
            logging.debug("User.create_task: {0}, {1}, {2}".format(self.task.project, self.task.summary, self.task.task_text))
            issue=jira.create_issue(jf)
            for filename in self.task.file:
                jira.add_attachment(issue=issue, attachment=filename)
            f=open(db_dir+self.task.task_id,'w')
            f.write(issue.id)
            f.close()
            query = update.callback_query
            query.edit_message_text(text=task_was_created_message[self.language].format(self.format_url(issue.key), self.task.task_to.name), parse_mode=ParseMode.MARKDOWN)
            #keys=ReplyKeyboardMarkup(keyboard=[[comm for comm in init_commands[self.language].values()]], resize_keyboard=True)
            #self.bot.sendMessage(chat_id=update.message.chat_id, text=task_was_created_message[self.language].format(self.format_url(issue.key),
            #                self.task.task_to.name), reply_markup=ReplyKeyboardRemove(), parse_mode=ParseMode.MARKDOWN)
            self.reset()
        else:
            keys=ReplyKeyboardMarkup(keyboard=[[comm for comm in init_commands[self.language].values()]], resize_keyboard=True)
            self.bot.sendMessage(chat_id=update.message.chat_id, text=no_text_message[self.language], reply_markup=keys)
    
    def list_tasks(self, bot, update, jira):
        answer=''
        answer+='<b>'+jirauser_assignee_list[self.language].format(self.name)+':</b>\n'
        issues=jira.search_issues('assignee={0} and status!=Done'.format(self.jirauser))
        for issue in issues:answer+='• <a href="'+jiraserver+'/browse/'+issue.key+'">'+\
        str(issue.key)+'</a> (<i>'+issue.raw['fields']['status']['name']+'</i>) '+issue.raw['fields']['summary']+'\n'
        answer+='\n<b>'+jirauser_author_list[self.language].format(self.name)+':</b>\n'
        issues=jira.search_issues('reporter={0} and status!=Done'.format(self.jirauser))
        for issue in issues:answer+='• <a href="'+jiraserver+'/browse/'+issue.key+'">'+\
        str(issue.key)+'</a> (<i>'+issue.raw['fields']['status']['name']+'</i>) '+issue.raw['fields']['summary']+'\n'
        bot.sendMessage(chat_id=update.message.chat_id, text=answer, parse_mode='HTML')
        keys=ReplyKeyboardMarkup(keyboard=[[comm for comm in init_commands[self.language].values()]], resize_keyboard=True)
        bot.sendMessage(chat_id=update.message.chat_id, text=hello_message[self.language], reply_markup=keys)

    def reset(self):
        self.summary=None
        self.task_summary_set=False
        self.task_priority_set=False
        self.task_deadline_set=False
        self.task_project_set=False
        self.task_assignee_set=False
        self.createtask=False
        self.send_task=False
        self.task=None
        self.bot=None

    def format_url(self, issue_id):
        return '[{0}]({1}/browse/{0})'.format(issue_id, jiraserver)