# _*_ coding:utf-8 _*_
#@Author = zhoupengfei
#@Time = 2018/11/30 17:08
from django.conf.urls import url,include
from rest_framework.routers import DefaultRouter
from .views import UesrLoginview ,AddQuestionView,CheckQuestionViews,DeleteQuestion,EditorQuestion,SwitchPosition,ScoreAssessView
from .views import UserActionView,SetUpPassView,SearchOneDataView,SerachTeamView,RecordActionView,ClickrecordView,QueryMixCode
from .views import QueryClick,UploadPicture,AddArticleView,ToviewData,Removecontent,BackEditview,CasePushView,CollectionView
from .views import LookregulationsView,DeletePicture,UploadFileView,CheckCauseView,CheckadministrationView,CheckArticleview,Cancelcollectionview
from .views import SelectArticle,AddAnnotationView,LookAllannotationView,DeleteannotationView,QueryannotationByid
router = DefaultRouter()
app_name = "api"
urlpatterns = [
    url(r'^login/',UesrLoginview.as_view(),name='login'),
    url(r'^addquestion/', AddQuestionView.as_view(),name='addquestion'),
    url(r'^questions/',CheckQuestionViews.as_view({'get': 'list'}),name='questions'),
    url(r'^deletequestion/', DeleteQuestion.as_view(),name='deletequestion'),
    url(r'^editquestion/', EditorQuestion.as_view(),name='editquestion'),
    url(r'^transposition/', SwitchPosition.as_view(),name='transposition'),
    url(r'^scoreassess/', ScoreAssessView.as_view(),name='scoreassess'),
    url(r'^action/', UserActionView.as_view(),name='action'),
    url(r'^setup/', SetUpPassView.as_view(),name='setup'),
    url(r'^searchone/', SearchOneDataView.as_view(),name='searchone'),
    url(r'^searchteam/', SerachTeamView.as_view(),name='searchteam'),
    url(r'^record/', RecordActionView.as_view(),name='record'),
    url(r'^click/', ClickrecordView.as_view(), name='click'),
    url(r'^querycode/', QueryMixCode.as_view(), name='querycode'),
    url(r'^queryclick/', QueryClick.as_view(), name='queryclick'),
    url(r'^picture/', UploadPicture.as_view(), name='picture'),
    url(r'^addcontent/', AddArticleView.as_view(), name='addcontent'),
    url(r'^toview/', ToviewData.as_view(), name='toview'),
    url(r'^removecontent/', Removecontent.as_view(), name='removecontent'),
    url(r'^backedit/', BackEditview.as_view(), name='backedit'),
    url(r'^causepush/', CasePushView.as_view(), name='causepush'),
    url(r'^collection/', CollectionView.as_view(), name='collection'),
    url(r'^lookcollection/', LookregulationsView.as_view(), name='lookcollection'),
    url(r'^checkcause/', CheckCauseView.as_view(), name='checkcause'),
    url(r'^lookadministration/', CheckadministrationView.as_view(), name='lookadministration'),
    url(r'^checkarticle/', CheckArticleview.as_view(), name='checkarticle'),
    url(r'^undockpicture/', DeletePicture.as_view(), name='undockpicture'),
    url(r'^uploadfile/', UploadFileView.as_view(), name='uploadfile'),
    url(r'^cancelcollection/', Cancelcollectionview.as_view(), name='cancelcollection'),
    url(r'^article/', SelectArticle.as_view(), name='article'),
    url(r'^addannotation/', AddAnnotationView.as_view(), name='addannotation'),
    url(r'^allannotation/', LookAllannotationView.as_view({'get': 'list'}), name='allannotation'),
    url(r'^moveannotation/', DeleteannotationView.as_view(), name='moveannotation'),
    url(r'^queryannotation/', QueryannotationByid.as_view(), name='queryannotation'),
    url(r'', include(router.urls)),
]