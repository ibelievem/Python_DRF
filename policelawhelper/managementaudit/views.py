from django.shortcuts import render

# Create your views here.
import datetime,os,time,re,requests,json,uuid
from rest_framework import views
from django.http import JsonResponse
from .lib import exceptionlib,responselib
from .models import UserLogin, Question, Passnum, ActionAnalyze,ClickRecord,MixCode,Picture,HelperData,PlotLabel,Collection,UploadFile
from .models import TrafficArticle,ArticleStatics,Annotation,Daojiao_lawsearch_code
from rest_framework import filters
from rest_framework import viewsets
from rest_framework import mixins,generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from .serializers import QuestionSerializer,AnnotationSerializer
from policelawhelper import settings
from django.core.paginator import Paginator
from django.conf import settings


helper_logger = settings.LOG

class UesrLoginview(views.APIView):
    '''
    用户登录功能
    '''
    @responselib.exception_handler
    def post(self, request):
        phone = request.data.get('phone')
        name = request.data.get('name')
        police_code = request.data.get('police_code')
        group_name = request.data.get('group_name')
        type = request.data.get('type')
        result = responselib.init_response_data()
        if name == "" or police_code == "" or group_name == "" or type == "":
            helper_logger.error("用户输入信息不完整")
            raise exceptionlib.CustomException('用户输入信息不完整')
        user_data = UserLogin.objects.filter(phone=phone)
        if user_data:
            if user_data[0].name!= name:
                raise  exceptionlib.CustomException('姓名与初次登陆手机号码不符')
            elif user_data[0].Police_code!= police_code:
                raise exceptionlib.CustomException('警编与初次登陆手机号码不符')
            else:
                result['data'] = "登陆成功"
        else:
            user_obj = UserLogin(phone=phone, name=name, Police_code=police_code, Group_name=group_name, type=type)
            user_obj.save()
            result['data'] = "登录成功"
        return JsonResponse(result)


class AddQuestionView(views.APIView):
#     '''
#     后台增加问题接口
#     '''
    @responselib.exception_handler
    def post(self, request):
        question = request.data.get('question')
        tags = request.data.get('tags')
        tags= eval(tags)
        type = request.data.get('type')
        answer = request.data.get('answer')
        result = responselib.init_response_data()
        if type == "":
            helper_logger.error("请选择问题类型")
            raise exceptionlib.CustomException('请选择问题类型')
        if answer == "":
            helper_logger.error("答案不能为空")
            raise exceptionlib.CustomException('答案不能为空')
        if len(tags)!=4:
            helper_logger.error("请将选项补充完整")
            raise exceptionlib.CustomException('请将选项补充完整')
        question_data = Question.objects.filter(question=question)
        if question_data:
            raise exceptionlib.CustomException('问题已经存在')
        else:
            question_obj = Question(question=question,type=type,answer=answer,A=tags[0],B=tags[1],C=tags[2],D=tags[3])
            question_obj.save()
            result['data'] = "问题录入成功"
        return JsonResponse(result)


class QuestionPagination(PageNumberPagination):
    '''
    分页
    '''
    page_size = 5
    page_size_query_param = 'page_size'
    page_query_param = 'p'
    max_page_size = 30

    def get_paginated_response(self, data):
        """
        设置返回内容格式
        """
        return JsonResponse({
            'results': data,
            'count': self.page.paginator.count,
            'page_size': self.page.paginator.per_page,
            'page': self.page.start_index() // self.page.paginator.per_page + 1,
            'next':self.get_next_link(),
            'previous':self.get_previous_link(),
        })


class CheckQuestionViews(mixins.ListModelMixin,viewsets.GenericViewSet):
    '''
    查看状态为0 的用户反馈
    '''
    queryset = Question.objects.filter(is_enable="1")
    serializer_class = QuestionSerializer
    pagination_class = QuestionPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    # ordering_fields = ('create_time')


class DeleteQuestion(views.APIView):
    '''
    删除问题
    '''
    @responselib.exception_handler
    def get(self, request):
        question_id = request.GET.get('qid')
        result = responselib.init_response_data()
        question_obj = Question.objects.filter(id=question_id)
        print(question_obj)
        if question_obj:
            question_obj.delete()
            result['data'] = "问题删除成功"
        else:
            helper_logger.error("删除失败")
            raise exceptionlib.CustomException('删除失败')
        return JsonResponse(result)


class EditorQuestion(views.APIView):
    '''
    编辑问题
    '''

    @responselib.exception_handler
    def post(self, request):
        qid = request.data.get('qid','')
        question = request.data.get('question')
        tags = request.data.get('tags')
        tags = eval(tags)
        type = request.data.get('type')
        answer = request.data.get('answer')
        result = responselib.init_response_data()
        if qid =='':
            helper_logger.error("问题id错误")
            raise exceptionlib.CustomException('问题id错误')
        question_data = Question.objects.get(id=qid)
        question_data.question=question
        question_data.A=tags[0]
        question_data.B = tags[1]
        question_data.C = tags[2]
        question_data.D = tags[3]
        question_data.type = type
        question_data.answer=answer
        question_data.save()
        result['data'] = "问题修改成功"
        return JsonResponse(result)


class SwitchPosition(views.APIView):
    '''
    问题位置调换接口
    '''
    @responselib.exception_handler
    def post(self, request):
        current_qid = request.data.get('currentqid')
        currenttime = request.data.get('currenttime')
        other_qid = request.data.get('otherqid')
        othertime = request.data.get('othertime')
        result = responselib.init_response_data()
        current_question = Question.objects.get(id=current_qid)
        other_question = Question.objects.get(id=other_qid)
        current_question.create_time = othertime
        current_question.save()
        other_question.create_time =currenttime
        other_question.save()

        result['data'] = "位置调换成功"
        return JsonResponse(result)


class ScoreAssessView(views.APIView):
    '''
    成绩评测
    '''
    @responselib.exception_handler
    def post(self, request):
        phone = request.data.get('phone')
        grade_list = request.data.get('result')
        grade_list=eval(grade_list)
        result = responselib.init_response_data()
        # qids = [qid["id"] for qid in grade_list]
        num_obj = Passnum.objects.get(id=1)
        passnum = num_obj.num
        wrong = 0
        right = 0
        parms={}
        for qid in grade_list:
            current_question = Question.objects.get(id=qid['id'])
            if qid['answer']== current_question.answer:
                right+=1
            elif qid['answer']!= current_question.answer:
                wrong+=1
        if right >=passnum:
            parms['right'] = right
            parms['wrong'] = wrong
            parms['is_pass'] = "是"
            user_data = UserLogin.objects.get(phone=phone)
            user_data.grade = "是"
            user_data.save()
        elif right < passnum:
            parms['right'] = right
            parms['wrong'] = wrong
            parms['is_pass'] = "否"
            user_data = UserLogin.objects.get(phone=phone)
            user_data.grade = "否"
            user_data.save()
        result['data'] = parms
        return JsonResponse(result)


class UserActionView(views.APIView):
    '''
    用户行为分析
    '''
    @responselib.exception_handler
    def get(self,request):
        result = responselib.init_response_data()
        action = {}
        now_time = datetime.datetime.now()
        change_time = now_time + datetime.timedelta(days=-7)
        user_time = UserLogin.objects.filter(create_time__gte=str(change_time))
        add_user_num = round(len(user_time)/7,False)
        action['add_user_num']=add_user_num
        user_obj = UserLogin.objects.filter()
        all_user = len(user_obj)
        action['all_user']=all_user
        action_obj = ActionAnalyze.objects.filter()
        open_num = round(len(action_obj)/7,False)
        action['open_num'] = open_num
        m=0
        for time in action_obj:
            time.stay_time+=m
        use_time = round(m/60/7,False)
        action['use_time'] = use_time
        active_num = 0
        action['active_num'] = active_num
        result['data'] = action

        return JsonResponse(result)


class SetUpPassView(views.APIView):
    '''
        设置过关题目数量
        '''
    @responselib.exception_handler
    def post(self, request):
        num = request.data.get('num')
        result = responselib.init_response_data()
        num_obj = Passnum.objects.get(id=1)
        num_obj.num=num
        num_obj.save()
        result['data'] = "保存成功"
        return JsonResponse(result)


class SearchOneDataView(views.APIView):
    '''
    查询具体人员情况
    '''
    @responselib.exception_handler
    def post(self, request):
        phone = request.data.get('phone')
        name = request.data.get('name')
        police_code = request.data.get('police_code')
        result = responselib.init_response_data()
        message = {}
        try:
            user_obj = UserLogin.objects.get(phone=phone,name=name,Police_code=police_code)
        except:
            helper_logger.error("查询失败，请检查信息填写是否准确！")
            raise exceptionlib.CustomException('查询失败，请检查信息填写是否准确！')
        message['name'] = name
        message['phone'] = phone
        message['type'] = user_obj.type
        message['police_code'] = police_code
        message['is_pass'] = user_obj.grade
        result['data'] = message
        return JsonResponse(result)


class SerachTeamView(views.APIView):
    '''
    查询具体大队名称
    '''
    def get(self, request):
        group_name = request.GET.get('group_name')
        result = responselib.init_response_data()
        userLogin_obj = UserLogin.objects.filter(Group_name=group_name)
        team_data = {}
        if userLogin_obj:
            Login_obj = UserLogin.objects.filter(Group_name=group_name,grade="是")
            # print(Login_obj)
            pass_num= len(Login_obj)
            if pass_num != 0:
                a = pass_num/len(userLogin_obj)
                bb = "%.2f%%" % (a * 100)
                team_data['pass_rate'] = bb
            elif pass_num==0:
                team_data['pass_rate'] = "暂无通过考试详情"
            team_data['name'] = group_name
            team_data['join_num'] = len(userLogin_obj)
            result['data'] = team_data
        else:
            helper_logger.error("查询失败，暂无该队相关信息！")
            raise exceptionlib.CustomException('暂无该队相关信息')
        return JsonResponse(result)


class RecordActionView(views.APIView):
    '''
    记录用户行为接口
    '''
    @responselib.exception_handler
    def post(self, request):
        phone = request.data.get('phone')
        stay_time = request.data.get('stay_time')
        result = responselib.init_response_data()
        now_time = datetime.datetime.now()
        change_time = now_time + datetime.timedelta(days=-7)
        record_obj = ActionAnalyze(phone=phone,stay_time=stay_time,use_num=1)
        record_obj.save()
        delete_obj = ActionAnalyze.objects.filter(create_time__lte=str(change_time))
        delete_obj.delete()
        result['data'] = '记录成功'
        return JsonResponse(result)


class ClickrecordView(views.APIView):
    '''
       模块点击记录
       '''
    @responselib.exception_handler
    def post(self, request):
        module_name = request.data.get('module_name')
        click_num = request.data.get('click_num')
        result = responselib.init_response_data()
        data_obj = ClickRecord.objects.filter(module_name=module_name)
        if data_obj:
            module_data = ClickRecord.objects.get(module_name=module_name)
            module_data.click_num = module_data.click_num+ int(click_num)
            module_data.save()
        else:
            click_obj = ClickRecord(module_name=module_name,click_num=click_num)
            click_obj.save()
            print("记录成功")
        all_click_obj = ClickRecord.objects.all()
        module_click = []
        for item in all_click_obj:
            module = {}
            module['module_name'] = item.module_name
            module['click_num'] = item.click_num
            module_click.append(module)
        result['data'] = module_click
        return JsonResponse(result)


class QueryMixCode(views.APIView):
    '''
           查询混淆码
           '''
    @responselib.exception_handler
    def post(self, request):
        mix_code = request.data.get('mix_code')
        result = responselib.init_response_data()
        mix_data = {}
        try:
            code_obj = MixCode.objects.get(mix_code=int(mix_code))
        except:
            helper_logger.error("查询失败")
            raise exceptionlib.CustomException('未查询到相关数据')
        code_mix_obj = MixCode.objects.get(mix_code=0)
        content = code_obj.content
        mix_data['content'] = content
        mix_data['all_content'] = code_mix_obj.content
        mix_data['mix_code'] = "<em>" + mix_code + "</em>"
        result['data'] = mix_data
        return JsonResponse(result)


class QueryClick(views.APIView):
    '''
               pc端点击记录查询
               '''
    @responselib.exception_handler
    def get(self, request):
        result = responselib.init_response_data()
        all_click_obj = ClickRecord.objects.all()
        module_click = []
        num = 0
        for item in all_click_obj:
            module = {}
            module['module_name'] = item.module_name
            module['click_num'] = item.click_num
            num = item.click_num + num
            module_click.append(module)
        average_num = round(num/7,False)
        module_click.append({'average_num':average_num})
        result['data'] = module_click
        return JsonResponse(result)


class UploadPicture(views.APIView):
    '''
    上传图片接口
    '''
    @responselib.exception_handler
    def post(self, request):
        charge_id = request.data.get('charge_id')
        kind_name = request.data.get('kind_name')
        title = request.data.get('title')
        photo = request.data["picture"].read()
        result = responselib.init_response_data()
        upload_path1 = os.path.join(settings.BASE_DIR, "media/images/")
        if not os.path.exists(upload_path1):
            os.makedirs(upload_path1)
        a = str(int(time.time()))
        upload_path = os.path.join(upload_path1, a + ".png")
        with open(upload_path, 'wb') as f:
            f.write(photo)
        user_info_data_dict = {}
        new_path = re.match('.*?(/images/\d+\.png)', upload_path).group(1)
        new_path = "/media" + new_path
        image_obj = Picture.objects.filter(charge_id=charge_id,kind_name=kind_name)
        if image_obj:
            image_obj = Picture.objects.get(charge_id=charge_id, kind_name=kind_name)
            image_obj.title = title
            image_obj.content = new_path
            image_obj.save()
        else:
            picture_obj = Picture(charge_id=charge_id,kind_name=kind_name,title=title,content=new_path)
            picture_obj.save()
        user_info_data_dict["picture"] = new_path
        result['data'] = user_info_data_dict
        print( result['data'])
        return JsonResponse(result)


class AddArticleView(views.APIView):
    '''
    录入内容接口
    '''
    @responselib.exception_handler
    def post(self, request):
        charge_id = request.data.get('charge_id')
        kind_name = request.data.get('kind_name')
        title = request.data.get('title')
        content = request.data.get('content')
        result = responselib.init_response_data()
        content_obj = HelperData.objects.filter(charge_id=charge_id,kind_name=kind_name,title=title)
        if content_obj:
            content_obj = HelperData.objects.get(charge_id=charge_id, kind_name=kind_name, title=title)
            content_obj.content = content
            content_obj.save()
        else:
            picture_obj = HelperData(charge_id=charge_id,kind_name=kind_name,title=title,content=content)
            picture_obj.save()
        result['data'] = "录入成功"
        return JsonResponse(result)


class ToviewData(views.APIView):
    '''
    查看图片和内容
               '''
    @responselib.exception_handler
    def post(self, request):
        charge_id = request.data.get('charge_id')
        kind_name = request.data.get('kind_name')
        result = responselib.init_response_data()
        message = []
        try:
            image_obj = Picture.objects.get(charge_id=charge_id, kind_name=kind_name)
            picture = image_obj.content
            title = image_obj.title
            message.append({"type":1,"content":str(picture),"title":title})
        except:
            message.append({"type": 1, "content": None, "title": None})
        content_obj = HelperData.objects.filter(charge_id=charge_id, kind_name=kind_name)
        for item in content_obj:
            module = {}
            module['type'] = 2
            module['id'] = item.id
            module['title'] = item.title
            module['content'] = item.content
            message.append(module)


        file_obj = UploadFile.objects.filter(charge_id=charge_id, kind_name=kind_name)
        for ls in file_obj:
            file_dict = {}
            file_dict['type'] = 3
            file_dict['title'] = ls.title
            file_dict['file_path'] = str(ls.file)
            message.append(file_dict)
        result['data'] = message
        return JsonResponse(result)


class Removecontent(views.APIView):
    '''
    删除内容
               '''
    @responselib.exception_handler
    def post(self, request):
        id = request.data.get('id')
        result = responselib.init_response_data()
        question_obj = HelperData.objects.filter(id=id)
        if question_obj:
            question_obj.delete()
            result['data'] = "问题删除成功"
        else:
            helper_logger.error("删除失败")
            raise exceptionlib.CustomException('删除失败')
        return JsonResponse(result)


class BackEditview(views.APIView):
    '''
        编辑内容
    '''
    @responselib.exception_handler
    def post(self, request):
        title = request.data.get('title')
        id = request.data.get('id')
        content = request.data.get('content')
        if id == "":
            helper_logger.error("id错误")
            raise exceptionlib.CustomException('id错误')
        result = responselib.init_response_data()
        question_obj = HelperData.objects.get(id=id)
        question_obj.title = title
        question_obj.content = content
        question_obj.save()
        result['data'] = "修改成功"
        return JsonResponse(result)


class CasePushView(views.APIView):
    """
    点选情节，推送类案
    """
    @responselib.exception_handler
    def post(self, request):
        tags = request.data.get('tags')
        tags = eval(tags)
        page = request.data.get('page')
        result = responselib.init_response_data()
        if page is None:
            page = '1'
        tag_ids = ""
        for tag in tags:
            plotlabel = PlotLabel.objects.get(tag_name=tag)
            tag_id = plotlabel.tag_id
            tag_ids += "&tags=%s" % tag_id
        # pages = "page="
        url = 'http://related.aegis-info.com/api/case/tag?page='+page+'&size=10' + tag_ids
        # response = requests.get('http://192.168.11.248:8111/api/case/tag?page=1&size=10' + tag_ids)
        try:
            response = requests.get(url)
            json_data=json.loads(response.text)
            total = json_data["pager"]["total"]
        except Exception as e:
            helper_logger.error(e)
        for cause in json_data["data"]["causeList"]:
            num = cause["num"]
            percentage = "%.1f%%" % (num / total * 100)
            cause["percentage"] = percentage
        result['data'] = json_data["data"]
        result["pager"] = json_data["pager"]
        return JsonResponse(result)


class CollectionView(views.APIView):
    """
    收藏
    """
    @responselib.exception_handler
    def post(self, request):
        phone = request.data.get('phone')
        article_id = request.data.get('article_id')
        type = request.data.get("type")
        result = responselib.init_response_data()
        if phone == "" or phone ==None:
            helper_logger.error('手机号不能为空')
            raise exceptionlib.CustomException('手机号不能为空')
        if article_id == "" or article_id ==None:
            helper_logger.error('文章id不能为空')
            raise exceptionlib.CustomException('文章id不能为空')
        shoucang_obj = Collection.objects.filter(phone=phone,article_id=article_id)
        if shoucang_obj:
            raise exceptionlib.CustomException('重复收藏')
        else:
            collection_data = Collection(phone=phone,article_id=article_id,type=type)
            collection_data.save()
            result['data'] = "收藏成功"
        return JsonResponse(result)


class LookregulationsView(views.APIView):
    '''
    查询法律法规收藏
    '''
    @responselib.exception_handler
    def get(self, request):
        phone = request.GET.get('phone')
        result = responselib.init_response_data()
        collection = Collection.objects.filter(phone=phone,type="法律法规")

        regulations = []
        for item in collection:
            code_obj = Daojiao_lawsearch_code.objects.using('daojiao').get(id=item.article_id)
            url = "http://lawsearch.aegis-info.com/law_search/law/detail?id="+str(code_obj.name_md5_id)
            response = requests.post(url)
            json_data = json.loads(response.text)
            re_law = json_data.get('data', {})
            re_law['id'] = item.id
            regulations.append(re_law)
        result['data'] = regulations
        return JsonResponse(result)


class CheckCauseView(views.APIView):
    '''
        查询相关案例收藏
        '''
    @responselib.exception_handler
    def get(self, request):
        phone = request.GET.get('phone')
        result = responselib.init_response_data()
        cause_obj = Collection.objects.filter(phone=phone, type="相关案例")
        cause_list = []
        for case in cause_obj:
            url_case = "http://test.traffic.xcases.aegis-info.com/xcases/v1/search/" + str(case.article_id)
            data_cause = requests.get(url_case)
            json_obj = json.loads(data_cause.text)
            cause = json_obj.get('data', {})
            cause['id'] = case.id
            cause_list.append(cause)
        result['data'] = cause_list
        return JsonResponse(result)


class CheckadministrationView(views.APIView):
    '''
        查询行政诉讼收藏
        '''
    @responselib.exception_handler
    def get(self, request):
        phone = request.GET.get('phone')
        result = responselib.init_response_data()
        litigation_obj = Collection.objects.filter(phone=phone, type="行政诉讼")
        litigation_list = []
        for stration in litigation_obj:
            url_litigation = "http://searchservice.aegis-info.com/case/query/queryForTrafficDetail?caseId=" + stration.article_id
            administration = requests.get(url_litigation)
            json_stration = json.loads(administration.text)
            administrativelitigation = json_stration.get('data', {})
            administrativelitigation['id'] = stration.id
            litigation_list.append(administrativelitigation)
        result['data'] = litigation_list
        return JsonResponse(result)


class CheckArticleview(views.APIView):
    '''
        查询相关文章收藏
        '''
    @responselib.exception_handler
    def get(self, request):
        phone = request.GET.get('phone')
        result = responselib.init_response_data()
        litigation_obj = Collection.objects.filter(phone=phone, type="相关文章")
        if litigation_obj:
            article_list = []
            for stration in litigation_obj:
                article = {}
                article_obj = TrafficArticle.objects.get(id=stration.article_id)
                article['id'] = stration.id

                article['title']=article_obj.article_title
                article['content'] =eval(article_obj.article_content)
                article_list.append(article)
            result['data'] = article_list
        else:
            helper_logger.error('暂无文章')
            raise exceptionlib.CustomException('暂无文章')
        return JsonResponse(result)


class DeletePicture(views.APIView):
    '''
    删除内容
               '''
    @responselib.exception_handler
    def get(self, request):
        id = request.GET.get('pid')
        result = responselib.init_response_data()
        picture_obj = Picture.objects.filter(id=int(id))
        print(picture_obj)
        if picture_obj:
            picture_obj.delete()
            result['data'] = "图片删除成功"
        else:
            helper_logger.error('删除失败')
            raise exceptionlib.CustomException('删除失败')
        return JsonResponse(result)


class UploadFileView(views.APIView):
    '''
        上传文件接口
        '''
    @responselib.exception_handler
    def post(self, request):
        charge_id= request.data.get('charge_id')
        kind_name=request.data.get('kind_name')
        title = request.data.get('title','')
        file = request.FILES.get('file')
        if file == None:
            raise exceptionlib.CustomException('没有文件可以上传')
        result = responselib.init_response_data()
        upload_path1 = os.path.join(settings.BASE_DIR, "media/files/")
        if not os.path.exists(upload_path1):
            os.makedirs(upload_path1)
        # a = str(int(time.time()))
        upload_path = os.path.join(upload_path1,file.name)
        try:
            fin = open(upload_path, "wb")
            fin.write(file)
        except Exception as e:
            helper_logger.error(e)
        new_path = re.findall(r'policelawhelper/(.*?)$', upload_path)[0]
        UploadFile_obj = UploadFile(charge_id=charge_id,kind_name=kind_name,title=title,file=new_path)
        UploadFile_obj.save()

        result['data'] = "上传成功"
        return JsonResponse(result)


class Cancelcollectionview(views.APIView):
    '''
    删除内容
               '''
    @responselib.exception_handler
    def get(self, request):
        id = request.GET.get('id')
        result = responselib.init_response_data()
        try:
            litigation_obj = Collection.objects.get(id=id)
            if litigation_obj:
                litigation_obj.delete()
                result['data'] = "取消成功"
        except Exception as e:
            helper_logger.error(e)
            raise exceptionlib.CustomException('取消失败')
        return JsonResponse(result)


class SelectArticle(views.APIView):
    """
    关键词，文章查询
        公安部置顶，后续以发布时间排序
    """
    @responselib.exception_handler
    def post(self, request):
        keyword = request.data.get("keyword")
        page = request.data.get("page")
        if page is None:
            page = '1'
        articles = TrafficArticle.objects.filter(article_title__contains=keyword)
        if articles.count() != 0:
            articles_total = Paginator(articles, 10)
            if int(page) > int(len(articles_total.object_list) / 10) + 1:
                page = str(int(len(articles_total.object_list) / 10) + 1)
            articles = articles_total.page(page)
            result = responselib.init_response_data()
            article_list = []
            for i in articles.object_list:
                id  = i.id
                article_title = i.article_title
                publish_time = i.publish_time
                issuing_agency = i.issuing_agency
                article_content = i.article_content
                soucrce_url = i.soucrce_url
                article_content = eval(article_content)
                type_2 = [x for x in article_content if x["type"] >= 2]
                if type_2:
                    for article_text in article_content:
                        if article_text["type"] == 2:
                            img_name = ''
                            if "mmbiz_" not in article_text["text"]:
                                img_name = re.findall(r"mmbiz/(.*?)/", article_text["text"])[0] + '.jpg'
                            elif "mmbiz_" in article_text["text"]:
                                img_name = re.findall(r"mmbiz_(.*?)$", article_text["text"])[0]
                                img_name = img_name.split("/")
                                img_name = img_name[1] + '.%s' % img_name[0]
                            img_path = ArticleStatics.objects.filter(static_file_name=img_name, article_id=id)
                            img_path = img_path[0].static_file_path
                            article_text["text"] = "media/article_pic/" + img_path.replace("\\", "/")
                        elif article_text["type"] == 3:
                            article_content.remove(article_text)
                else:
                    pass
                article = dict(
                    id=id,
                    article_title=article_title,
                    publish_time=publish_time,
                    issuing_agency=issuing_agency,
                    article_content=article_content,
                    soucrce_url=soucrce_url
                )
                article_list.append(article)
            print(len(article_list))
            article_list = sorted(article_list, key=lambda x: (x["issuing_agency"], x["publish_time"]), reverse=False)
        else:
            helper_logger.error("无搜索结果")
        data = {
            "article_list": article_list,
            "pager": {
                "page": page,
                "total": articles_total.count,
                "page_size": len(articles)
            },
        }
        result["data"] = data
        return JsonResponse(result)


class AddAnnotationView(views.APIView):
    """
    增加注释
    """
    @responselib.exception_handler
    def post(self, request):
        annotation = request.data.get('annotation')
        keywords = request.data.get('keywords')
        if keywords == "":
            helper_logger.error("没有要增加注释的词语")
            raise exceptionlib.CustomException('没有要增加注释的词语！')
        if annotation == "":
            helper_logger.error("没有要增加的注释内容")
            raise exceptionlib.CustomException('没有要增加的注释内容！')
        result = responselib.init_response_data()
        ed=uuid.uuid4()
        annotation_data = Annotation(id = ed,annotation=annotation,keywords=keywords)
        annotation_data.save()
        result['data'] = "增加成功"
        return JsonResponse(result)


class AnnotationPagination(PageNumberPagination):
    '''
    分页
    '''
    page_size = 10
    page_size_query_param = 'page_size'
    page_query_param = 'p'
    max_page_size = 1000

    def get_paginated_response(self, data):
        """
        设置返回内容格式
        """
        return JsonResponse({
            'results': data,
            'count': self.page.paginator.count,
            'page_size': self.page.paginator.per_page,
            'page': self.page.start_index() // self.page.paginator.per_page + 1,
            'next':self.get_next_link(),
            'previous':self.get_previous_link(),
        })

class LookAllannotationView(mixins.ListModelMixin,viewsets.GenericViewSet):
    '''
    查看全部注释
    '''
    queryset = Annotation.objects.filter()
    serializer_class = AnnotationSerializer
    pagination_class = AnnotationPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)


class DeleteannotationView(views.APIView):
    '''
    删除内容
               '''
    @responselib.exception_handler
    def get(self, request):
        id = request.GET.get('id')
        result = responselib.init_response_data()
        picture_obj = Annotation.objects.filter(id=int(id))
        if picture_obj:
            picture_obj.delete()
            result['data'] = "注释删除成功"
        else:
            helper_logger.error("id不存在")
            raise exceptionlib.CustomException('删除失败')
        return JsonResponse(result)


class QueryannotationByid(views.APIView):
    @responselib.exception_handler
    def get(self, request):
        id = request.GET.get('id')
        result = responselib.init_response_data()
        content = {}
        try:
            picture_obj = Annotation.objects.get(id=id)
            content['id'] = picture_obj.id
            content['annotation'] = picture_obj.annotation
            content['keywords'] = picture_obj.keywords
            result['data'] = content
        except Exception as e:
            helper_logger.error(str(e))
            raise exceptionlib.CustomException('查询失败')
        return JsonResponse(result)
