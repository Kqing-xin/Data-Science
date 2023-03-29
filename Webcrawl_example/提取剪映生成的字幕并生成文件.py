# -*- codeing = utf-8 -*-
# @time :2021/4/11 14:14
# @Author :玉衡Kqing
# @File   ：test_QQemail.py
# @Software:PyCharm
import json
import os
import time
import datetime

class KCJYSRT:

    def __init__(self):
        self.on_init()

    def on_init(self):
        self.load_setting()

    def load_setting(self):
        pass

    def start(self):
        draft_folders = self.find_draft_folders()
        if len(draft_folders) == 0:
            msg = '未找到草稿目录'
            self.write_log(msg)
            return

        for _ in draft_folders:
            self.process_draft(_)
            pass

    def run(self):
        self.start()

    def read_file(self, filename: str = '') -> str:
        with open(filename, "r", encoding='utf-8') as f:
            result = json.load(f)
            return result

    def write_file(self, file_name: str = '', file_str: str = ''):
        with open(file_name,'w', encoding='utf-8') as f:
            f.write(file_str)

    def write_log(self, message: str = ''):
        now = datetime.datetime.now().replace(microsecond=0)
        result = f"{now} {message}"
        print(result)

    def analyse_file(self, jy_json:dict) -> dict:
        texts = jy_json['materials']['texts']
        tracks = jy_json['tracks']
        subtitle_dic = {}
        for _text in texts:
            _key = _text['id']
            _value = {'content': _text['content']}
            subtitle_dic[_key] = _value
        for _track in tracks:
            segments = _track['segments']
            for segment in segments:
                _mid = segment['material_id']
                if _mid in subtitle_dic.keys():
                    subtitleInfo = subtitle_dic[_mid]
                    subtitleInfo['start'] = segment['target_timerange']['start']
                    subtitleInfo['duration'] = segment['target_timerange']['duration']
                    subtitle_dic[_mid] = subtitleInfo
        subtitle_dic = sorted(subtitle_dic.items(), key=lambda x: x[1]['start'], reverse=False)
        return subtitle_dic

    def convert_timestr(self, t:int=0) -> str:
        _t = 1000000
        res = ''
        ms = t % _t // 1000
        sec = t // _t % 60
        min = t // _t // 60 % 60
        hour = t // _t // 60 // 60
        res += "%02d" % hour + ':' + "%02d" % min + ':' + "%02d" % sec + ',' + "%03d" % ms
        return res

    def make_str(self, subtitles:dict) -> str:
        _srt = ''
        _counter = 1
        for subtitle in subtitles:
            _srt += str(_counter)
            _srt += '\n'
            _counter += 1
            start = self.convert_timestr(subtitle[1]['start'])
            end = self.convert_timestr(subtitle[1]['start'] + subtitle[1]['duration'])
            _srt += start + ' --> ' + end
            _srt += '\n'
            _srt += subtitle[1]['content']
            _srt += '\n'
            _srt += '\n'
        return _srt

    def make_txt(self, subtitles={}) -> str:
        _txt = ''
        for subtitle in subtitles:
            _txt += subtitle[1]['content']
            _txt += '\n'
        return _txt

    def find_draft_folders(self) -> list:

        root_folder = os.path.expanduser('~') + '\\AppData\\Local\\JianyingPro\\User Data\\Projects\\com.lveditor.draft'

        result = []
        if not os.path.exists(root_folder):
            return  result
        for folder in os.listdir(root_folder):
            draft_folder = os.path.join(root_folder, folder)
            if os.path.isdir(draft_folder):
                result.append(draft_folder)

        return result

    def get_title(self, draft_info:str) -> str:
        jy_json = self.read_file(draft_info)

        texts = jy_json['draft_materials'][0]
        t = texts['value'][0]
        t = t['file_Path']
        r = os.path.split(t)[-1]
        r = os.path.splitext(r)[0]

        time_stamp = str(int(time.time()))
        title = '_'.join([r, time_stamp])

        return title

    def process_draft(self, draft_folder:str=''):

        if not os.path.isdir(draft_folder):
            msg = "目录出错"
            self.write_log(msg)
            return

        draft = os.path.join(draft_folder, "draft.json")
        draft_info = os.path.join(draft_folder, "draft_meta_info.json")

        json_str = self.read_file(draft)
        subtitle_dic = self.analyse_file(json_str)

        subtitle_str = self.make_str(subtitle_dic)
        subtitle_txt = self.make_txt(subtitle_dic)

        input_title = self.get_title(draft_info)

        export_folder = os.path.expanduser('~') + '/Desktop/'
        export_folder = os.path.join(export_folder, '自动从剪映导出字幕')
        try:
            os.makedirs(export_folder)
        except:
            pass

        srt_title = str(input_title) + '.srt'
        srt_title = os.path.join(export_folder, srt_title)
        txt_title = str(input_title) + '.txt'
        txt_title = os.path.join(export_folder, txt_title)

        self.write_file(srt_title, subtitle_str)
        msg = '保存在 ' + srt_title
        self.write_log(msg)

        self.write_file(txt_title, subtitle_txt)
        msg = '保存在 ' + txt_title
        self.write_log(msg)

def main():
    jysrt = KCJYSRT()
    jysrt.start()

if __name__ == '__main__':
    main()
