import unittest
from domain.generation import GenerationInput
from domain.generation import GenerationService
from shared.settings import Settings

class TestGeneration(unittest.TestCase):

    def setUp(self):
        self.settings = Settings()
        self.generation_service = GenerationService(settings=self.settings)

    def test_generate_response(self):
        inputs = GenerationInput(
            query="Việt Nam ở vị trí nào trên bản đồ thế giới?",
            chat_history=[],
            retrieved_info=[
                {"content": r"Việt Nam là một quốc gia nằm ở khu vực Đông Nam Á, với diện tích khoảng 331.000 km² và dân số hơn 100 triệu người tính đến năm 2023. Trong năm này, tổng sản phẩm quốc nội (GDP) của Việt Nam đạt 430 tỷ USD, tăng trưởng 5,2% so với năm 2022, chủ yếu nhờ vào sự phát triển của ngành công nghiệp sản xuất và xuất khẩu. Các mặt hàng xuất khẩu chủ lực bao gồm dệt may, điện tử, và nông sản như cà phê và gạo. Thành phố Hồ Chí Minh là trung tâm kinh tế lớn nhất, đóng góp khoảng 25% GDP cả nước. Ngoài kinh tế, Việt Nam cũng ghi nhận những tiến bộ xã hội đáng kể. Tỷ lệ biết chữ đạt 98%, và tuổi thọ trung bình tăng lên 76 tuổi. Tuy nhiên, quốc gia này vẫn đối mặt với thách thức về ô nhiễm môi trường, đặc biệt ở các đô thị lớn như Hà Nội, nơi chỉ số chất lượng không khí (AQI) thường xuyên ở mức báo động. Chính phủ đã triển khai nhiều chính sách để thúc đẩy năng lượng tái tạo, với mục tiêu 20% điện năng từ năng lượng mặt trời và gió vào năm 2030.", 
                 "metadata": {"Nguồn": "Kinh tế và Xã hội Việt Nam năm 2023"}
                }
            ]
        )
        response = self.generation_service.process(inputs)
        print(response.response)

if __name__ == '__main__':
    unittest.main()
        