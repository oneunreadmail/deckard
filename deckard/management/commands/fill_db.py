import sys
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model, authenticate
from ...models import Post, Blog, BlogPost, Person

User = get_user_model()


class Command(BaseCommand):
    args = '<foo bar ...>'
    help = 'our help string comes here'

    def _create_users(self, users):
        for username, password, email, first_name, last_name in users:
            try:
                print("Creating user {}.".format(username))
                user = User.objects.create_user(username=username, email=email)
                user.set_password(password)
                user.save()

                assert authenticate(username=username, password=password)
                print("User {} successfully created.".format(username))

                person = Person.objects.get(user=user)
                person.first_name = first_name
                person.last_name = last_name
                person.save()
                print("Person {} {} successfully created.".format(first_name, last_name))
            except:
                print("There was a problem creating the user: {}.  Error: {}.".format(username, sys.exc_info()[1]))

    def _create_blogs(self, blogs):
        for name, authors in blogs:
            try:
                print("Creating blog {}.".format(name))
                users = [User.objects.get(username=author) for author in authors]
                persons = [Person.objects.get(user=user) for user in users]
                blog = Blog(name=name)
                blog.save()
                for person in persons:
                    blog.contributors.add(person)

                print("Blog {} successfully created.".format(name))

            except:
                print("There was a problem creating the blog: {}.  Error: {}.".format(name, sys.exc_info()[1]))

    def _create_posts(self, posts):
        for blogname, title, text in posts:
            try:
                print("Creating post {}.".format(title))
                blog = Blog.objects.get(name=blogname)
                post = Post(title=title, text=text, source_blog=blog)
                post.save()
                BlogPost(blog=blog, post=post).save()
                print("Post {} successfully created.".format(title))

            except:
                print("There was a problem creating the post: {}.  Error: {}.".format(title, sys.exc_info()[1]))

    def handle(self, *args, **options):

        users = [
            ('navalny', 'qwer1234', 'navalny@example.com', "Alexey", "Navalny"),
            ('katz', 'qwer1234', 'katz@example.com', "Maxim", "Katz"),
        ]
        blogs = [
            ("putinvor", ["navalny"]),
            ("lavochki", ["katz"]),
            ("democracy", ["katz", "navalny"]),
        ]
        posts = [
            ("putinvor", "Калининград - супер!", """Калининград прекрасен. Меня тут ещё и по городу провели — пара тысяч экскурсоводов.
Калининградская область — очень специальный город для любого политика, приехавшего проводить массовую встречу с избирателями. Митинговые традиции здесь ого-го какие. В своё время губернатора Бооса сняли, потому что народ на улицы пошёл. Всего за путинские времена тут аж пять губернаторов сменилось.
Надо соответствовать. Наш штаб не подвёл и всё организовал отлично. Хоть власти и вынудили частную площадку в самом центре города отказать нам в последний момент, мы организованно переместились в Южный парк и там устроили просто суперский митинг.
По крайней мере, я уезжаю отсюда совершенно воодушевленный, и это отличное завершение недели."""),
            ("lavochki", "Как самоуправляемые машины спасут сотни тысяч жизней", """Сейчас очень модная тема — самоуправляемые машины. Кто только над ними ни работает, некоторые автомобили без водителей уже ездят по городам. Поучившись в Шотландии, я стал ярым сторонником скорейшего внедрения автомобильных автопилотов и вот почему.
ДТП с человеческими жертвами на дорогах происходят в первую очередь из-за высокой толерантности общества и властей к возможности таких смертей. Например, в США ежегодно от ДТП погибает 35,000 человек (в России в 2016 погибло 20,308 человек). Цифры огромные, но все воспринимают такие смерти как естественное дело — типа, ну неправильно водят/ходят бараны всякие, вот и гибнут, естественный отбор.
Такое мнение для России не уникально — в 60-х годах ровно так же мыслили и вовсю сообщали это в газетах Великобритании. Об этом я писал свою магистерскую диссертацию, ещё будет об этом пост. В обществе, где автомобиль массово распространился относительно недавно, толерантность к смертям от него очень высокая (США тут исключение, там толерантность высока и сейчас).
В странах, где толерантность к смертям в ДТП низкая, и смертность остается очень низкой. Например, в Швеции 15 лет назад приняли программу Vision Zero, которая делает центром транспортной политики безопасность. Там много интересных принципов подхода к транспортному планированию, строительству и управлению."""),
        ]
        self._create_users(users)
        self._create_blogs(blogs)
        self._create_posts(posts)
