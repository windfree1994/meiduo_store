import base64
import pickle
from rest_framework import status
from goods.models import SKU
from .serializers import CartDeleteSerializer,CartSerailzier,CartSKUSerializer
from django.shortcuts import render
from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework.views import APIView
# Create your views here.
class CartView(APIView):
    """
    1.登陆数据保存在redis中 未登录保存在cookie中
    增加
    查询
    删除
    修改
    数据：sku_id,count,selected
    哈希保存  key：value 的对应关系
    放在set中  第一不会重复 第二 不会占用资源
    """

    # 如果用户伪造token,我们就获取不到用户的真实信息,会报401的错误
    # 所以我们重写这个方法, 重写这个方法的目的就是我们在 post,get,.. 方法中
    # 先获取 user 然后自己进行判断
    def perform_authentication(self, request):
        pass

    def post(self, request):

        """
        1. 获取用户提交的数据,然后进行数据校验
        2. 获取校验的数据
        3. 根据用户的状态进行判断
        登录用户保存到redis
            4.1 链接redis
            4.2 添加数据
            4.3 返回响应
        为登录用户保存到cookie中
            5.1 先获取cookie中的购物车数据,判断是否存在
            5.2 如果存在就合并,如果不存在就添加
            5.3 返回响应


        """
        # 1. 获取用户提交的数据,然后进行数据校验
        serialzier = CartSerailzier(data=request.data)
        # is_valid 才是进行校验
        serialzier.is_valid()

        # 2获取校验的数据
        sku_id = serialzier.data.get('sku_id')
        count = serialzier.data.get('count')
        selected = serialzier.data.get('selected')

        # 3.如果用户伪造token,我们就获取不到用户的真实信息,会报401的错误
        # 所以我们需要捕获该异常,让user = None
        try:
            user = request.user
        except Exception:
            user = None

        # request.user.is_authenticated 判断用户是否登录
        # 判断user是否为none 同时判断是否为登录用户
        if user is not None and user.is_authenticated:
            # 登录用户

            # 4.1 连接redis
            redis_conn = get_redis_connection('cart')

            pl = redis_conn.pipeline()
            # 4.2 添加数据
            # redis  hash
            # redis_conn.hset('cart_%s'%user.id,sku_id,count)
            # pl.hset('cart_%s'%user.id,sku_id,count)

            # hincrby  第三个参数是一个增量
            # 例如: 原来 count是 5
            # 传了一个 1
            # 这个时候 count 6
            pl.hincrby('cart_%s' % user.id, sku_id, count)

            #       set
            if selected:
                # redis_conn.sadd('cart_selected_%s'%user.id,sku_id)
                pl.sadd('cart_selected_%s' % user.id, sku_id)

            pl.execute()
            # 4.3 返回响应
            return Response(serialzier.data)

        else:
            # 未登录用户
            # 5.1先获取cookie中的购物车数据, 判断是否存在
            cookie_str = request.COOKIES.get('cart')

            if cookie_str is not None:
                # cookie购物车不为空
                # 先 base64.b64decode
                # pickle.loads
                cart = pickle.loads(base64.b64decode(cookie_str))
                # cart = { 1: {'count':5,'selected':1} }
            else:
                # cookie购物车为空
                cart = {}

            # 5.2如果存在就合并, 如果不存在就添加
            # 判断 sku_id 有没有在 字典中
            if sku_id in cart:
                # 获取原来的count
                orgianl_count = cart[sku_id]['count']
                # 累加
                count += orgianl_count

            # 更新数据
            cart[sku_id] = {
                'count': count,
                'selected': selected
            }

            # 5.3返回响应

            response = Response(serialzier.data)

            # 将 字段转换
            # pickle.dumps
            # base64.b64encode()
            # decode()
            cookie_value = base64.b64encode(pickle.dumps(cart)).decode()

            response.set_cookie('cart', cookie_value, 7 * 24 * 60 * 60)

            return response

    def get(self, request):

        """
        1. 判断用户有没有登录
        2. 登录用户从redis中获取数据
            获取数据之后 查询商品的详细信息
        3. 未登录用户从cookie中获取数据(判断)
            如果存在数据 查询商品的详细信息
        4. 对商品的信息进行 JSON操作,返回响应

        """

        # 1.
        # 判断用户有没有登录
        try:
            user = request.user
        except Exception:
            user = None
        # request.user.is_authenticated
        if user is not None and user.is_authenticated:
            # 2.
            # 登录用户从redis中获取数据
            redis_conn = get_redis_connection('cart')
            # sku_id: count 的数据
            # {sku_id: count,sku_id: count,sku_id: count}
            redis_cart = redis_conn.hgetall('cart_%s' % user.id)
            # 选中的id
            redis_selected_ids = redis_conn.smembers('cart_selected_%s' % user.id)

            ## cart = {'id': {'count':4,'selected':1}}
            cart = {}
            for sku_id, count in redis_cart.items():
                # 注意: sku_id 和 count的类型 bytes类型
                # 我们对数据 最好进行强制类型转换

                # if sku_id in redis_selected_ids:
                #     selected = True
                # else:
                #     selected = False
                ##'selected': selected
                cart[int(sku_id)] = {
                    'count': int(count),
                    'selected': sku_id in redis_selected_ids

                }


        else:
            # 3.
            # cart = {'id': {'count':4,'selected':1}}
            # 未登录用户从cookie中获取数据(判断)

            cookie_str = request.COOKIES.get('cart')

            if cookie_str is not None:
                #
                cart = pickle.loads(base64.b64decode(cookie_str))
            else:
                cart = {}
        # 因一份为 cookie中 和 redis中 都要查询数据,所以我们把他们的数据做成一样的
        # 这样就可以把查询数据的代码写成 一份

        # 查询 redis 和 cookie 统一之后的数据

        # 获取所有商品的ids
        # 获取字典中所有的key
        # [1,2,3,4]
        sku_ids = cart.keys()

        skus = SKU.objects.filter(pk__in=sku_ids)
        # cart = {'id': {'count':4,'selected':1}}
        # 补充每个商品的 选中状态和数量
        for sku in skus:
            sku.count = cart[sku.id]['count']
            sku.selected = cart[sku.id]['selected']
        #
        #
        # 4.
        # 对商品的信息进行
        # JSON操作, 返回响应

        serializer = CartSKUSerializer(skus, many=True)

        return Response(serializer.data)


        # 5 +1 = 6 + 2 = 8 + -2


        # 6     4

    def put(self, request):

        """
        1. 用户提交数据,我们进行校验
        2. 获取校验后的数据
        3. 获取用户信息
            登录用户 更新redis
            为登录用户更新cookie
        """
        # 1. 用户提交数据,我们进行校验
        serializer = CartSerailzier(data=request.data)

        serializer.is_valid()
        # 2. 获取校验后的数据
        sku_id = serializer.data.get('sku_id')
        count = serializer.data.get('count')
        selected = serializer.data.get('selected')

        # 3. 获取用户信息
        try:
            user = request.user
        except Exception:
            user = None

        if user is not None and user.is_authenticated:
            # redis

            redis_conn = get_redis_connection('cart')

            # 更新数据, 我们是把购物车的数量的最终值 提交过来的,我们直接 更新数据
            redis_conn.hset('cart_%s' % user.id, sku_id, count)

            if selected:
                # 集合
                redis_conn.sadd('cart_selected_%s' % user.id, sku_id)

            return Response(serializer.data)

        else:

            # 获取数据并且判断
            cookie_str = request.COOKIES.get('cart')

            if cookie_str is not None:
                cart = pickle.loads(base64.b64decode(cookie_str))
            else:
                cart = {}

            # 更新数据
            # {'1': {'count':5,selected:1}}
            if sku_id in cart:
                cart[sku_id] = {
                    'count': count,
                    'selected': selected
                }

            # 返回响应
            response = Response(serializer.data)

            # 先 pickle.dumps
            # base64.b64encode()
            # decode()
            cookie_value = base64.b64encode(pickle.dumps(cart)).decode()

            response.set_cookie('cart', cookie_value, 7 * 24 * 3600)

            return response

    def delete(self, request):

        """
        1. 获取用户删除的id,并且进行判断
        2. 获取用户信息
        3. 登录用户 redis删除
        4. 未登录用户 cookie删除

        """

        # 1. 获取用户删除的id,并且进行判断
        serializer = CartDeleteSerializer(data=request.data)

        serializer.is_valid()

        sku_id = serializer.data.get('sku_id')

        # 2. 获取用户信息
        try:
            user = request.user
        except Exception:
            user = None

        if user is not None and user.is_authenticated:
            # 登录用户 redis删除

            redis_conn = get_redis_connection('cart')

            # 删除 hash中的数据 和 选中状态中的数据
            redis_conn.hdel('cart_%s' % user.id, sku_id)
            redis_conn.srem('cart_selected_%s' % user.id, sku_id)

            return Response(status=status.HTTP_204_NO_CONTENT)


        else:
            # 未登录用户 cookie删除

            cookie_str = request.COOKIES.get('cart')

            if cookie_str is not None:
                cart = pickle.loads(base64.b64decode(cookie_str))
            else:
                cart = {}

            # 判断是否在购物车中
            if sku_id in cart:
                # 在里边 就删除
                del cart[sku_id]

            response = Response(status=status.HTTP_204_NO_CONTENT)

            # dumps
            # base64.b64encode()
            # decode()
            cookie_value = base64.b64encode(pickle.dumps(cart)).decode()

            response.set_cookie('cart', cookie_value, 7 * 24 * 3600)

            return response
