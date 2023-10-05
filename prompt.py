
GPT_PROMPT_START = '''
Ты высококлассный программист на ruby.
Ты не учишь писать программы, ты их пишешь.
Ты пишешь программу в рамках проекта, работая в команде.
Ты пишешь полностью рабочий код, без сокращений и без отсылки к кому-либо.
Ты сам дописываешь все блоки кода.
Запрещено предлагать мне что-либо доделывать.
Ты всё доделываешь сам.
Ты сам пишешь повторяемые паттерны, методы и т.п.
В итоге должен получиться полностью рабочий тест.
Комментарии в коде запрещены.
Напиши отдельный тест для каждого метода.
Мета программирование запрещено.
Экономия места запрещена.
В рамках тестирования каждого метода, создай контекст для каждой из ролей используемой в тестируемом методе.
Учти, что пользователю с ролью Admin разрешено всё и всегда.
Доступ пользователей с ролью Admin, тоже нужно тестировать.
Не используй циклы.
Не сокращай код.
Аналогии запрещены, пиши весь код.
Напиши полный, рабочий код.
Напиши полностью рабочий тест, без сокращений и допущений.
Используй пример теста приведённый ниже и напиши тест для каждого метода, без исключений.
Пиши максимально близко к примеру.
Ничего не добавляй от себя.
Длина кода не ограничена.
И итоговом листинге должны быть приведены тесты всех методов, без исключений.

Вот пример теста:
# spec/policies/admin/admin_house_policy_spec.rb
require 'rails_helper'

RSpec.describe Admin::AdminHousePolicy, type: :policy do
  let(:user) { create(:user) }
  let(:context) { { user: } }
  let(:policy) { described_class.new(user:) }

  describe "#index?" do
    subject { policy.apply(:index?) }

    it "returns false when the user is not admin nor manager" do
      expect(subject).to be_falsey
    end

    context "when the user is an manager" do
      let(:user) { create(:user, :manager) }

      it { is_expected.to be_truthy }
    end
  end

  describe "#export?" do
    subject { policy.apply(:export?) }

    it "returns false when the user is not admin nor manager" do
      expect(subject).to be_falsey
    end

    context "when the user is an manager" do
      let(:user) { create(:user, :manager) }

      it { is_expected.to be_truthy }
    end
  end

  describe "#inactive?" do
    subject { policy.apply(:inactive?) }

    it "denies access to all users" do
      expect(subject).to be_falsey
    end
  end

  describe "#test_upload?" do
    subject { policy.apply(:test_upload?) }

    it "denies access to all users" do
      expect(subject).to be_falsey
    end
  end

  describe "#show?" do
    subject { policy.apply(:show?) }

    it "returns false when the user is not admin nor manager" do
      expect(subject).to be_falsey
    end

    context "when the user is an manager" do
      let(:user) { create(:user, :manager) }

      it { is_expected.to be_truthy }
    end
  end

  describe "#create?" do
    subject { policy.apply(:create?) }

    it "returns false when the user is not admin nor manager" do
      expect(subject).to be_falsey
    end

    context "when the user is an manager" do
      let(:user) { create(:user, :manager) }

      it { is_expected.to be_truthy }
    end
  end

  describe "#update?" do
    subject { policy.apply(:update?) }

    it "returns false when the user is not admin nor manager" do
      expect(subject).to be_falsey
    end

    context "when the user is an manager" do
      let(:user) { create(:user, :manager) }

      it { is_expected.to be_truthy }
    end
  end

  describe "#destroy?" do
    subject { policy.apply(:destroy?) }

    it "denies access to all users" do
      expect(subject).to be_falsey
    end
  end
end


Вводные данные:

class User < ApplicationRecord
  has_and_belongs_to_many :roles
  has_many :houses, foreign_key: 'owner_id'
  has_many :bookings, foreign_key: 'tenant_id'
  # has_many :statements, foreign_key: 'owner_id'
  has_many :jobs
  has_many :job_tracks, dependent: :destroy
  has_many :transactions
  has_many :booking_files, dependent: :nullify
  # has_many :jobs_created, class_name: 'Job', foreign_key: 'creator_id'
  has_many :todos
  has_many :todos_created, class_name: 'Todo', foreign_key: 'creator_id'

  scope :with_role, ->(role) { includes(:roles).where(roles: { name: role }) }
  scope :active_owners, -> { where('balance_closed = false') }
  scope :inactive_owners, -> { where('balance_closed = true') }

  def role?(role_or_roles)
    names = Array.wrap(role_or_roles).map(&:to_s).map(&:capitalize)
    !!roles.find_by(name: names)
  end

  def active_for_authentication?
    super && !balance_closed?
  end

  def inactive_message
    balance_closed? ? :inactive : super
  end

  def unpaid_bookings(booking_id = nil)
    if booking_id
      houses.joins(:bookings).where('(status != ? AND status != ? AND status != ?) OR bookings.id = ?',
                                    Booking.statuses[:paid], Booking.statuses[:block], Booking.statuses[:canceled], booking_id)
        .select('bookings.id', 'bookings.start', 'bookings.finish', 'houses.code')
        .order('bookings.start')
    else
      houses.joins(:bookings).where.not('bookings.status': [Booking.statuses[:paid], Booking.statuses[:block], Booking.statuses[:canceled]])
        .select('bookings.id', 'bookings.start', 'bookings.finish', 'houses.code')
        .order('bookings.start')
    end
  end

  # def is_any_of?(role)
  #   role = role.split = if role.kind_of?(String)
  #   result = false
  #   role.each do |r|

  #   end

  # end

  # Include default devise modules. Others available are:
  # :confirmable, :lockable, :timeoutable, :trackable and :omniauthable
  devise :database_authenticatable, :recoverable, # :registerable,
         :rememberable # , :validatable, :invitable, ,

  private

  def send_devise_notification(notification, *)
    devise_mailer.send(notification, self, *).deliver_later(priority: 0)
  end
end

class Role < ApplicationRecord
  has_and_belongs_to_many :users
end

FactoryBot.define do
  factory :user do
    email { Faker::Internet.email }
    password { "qweasd" }
    trait :admin do
      roles { [Role.find_or_create_by(name: 'Admin')] }
    end
    trait :manager do
      roles { [Role.find_or_create_by(name: 'Manager')] }
    end
    trait :accounting do
      roles { [Role.find_or_create_by(name: 'Accounting')] }
    end
    trait :owner do
      roles { [Role.find_or_create_by(name: 'Owner')] }
    end
    trait :client do
      roles { [Role.find_or_create_by(name: 'Client')] }
    end
  end
end

FactoryBot.define do
  factory :role do
    trait :admin do
      name { "Admin" }
    end
    trait :manager do
      name { "Manager" }
    end
    trait :acounting do
      name { "Accounting" }
    end
    trait :owner do
      name { "Owner" }
    end
    trait :client do
      name { "Client" }
    end
  end
end

class ApplicationPolicy < ActionPolicy::Base
  authorize :user, optional: true
  pre_check :allow_admins

  def index?
    false
  end

  def show?
    false
  end

  def create?
    false
  end

  def new?
    create?
  end

  def update?
    false
  end

  def edit?
    update?
  end

  def destroy?
    false
  end

  private

  def allow_admins
    allow! if user&.role? 'Admin'
  end
end


'''

GPT_PROMPT_END_METHOD = "Используя пример и приведённые данные, напиши тест для метода {method_name}, класса {class_name}. Предусмотри в тесте что проверку того, что роли Admin можно всё. Предусмотри в тесте проверку доступа неавторизованного пользователя. Неавторизованный пользователь, это пользователь без роли. Если в исходной политике разрешён доступ всем, то выводи только одну проверку на доступ неавторизованного пользователя. Используй только те роли пользователей которые указаны в методе политики и Admin. Приведи только блок describe. Пиши только код. Описание до или после кола запрещены."

RSPEC_START_1 = "# spec/policies/admin/admin_house_policy_spec.rb\nrequire 'rails_helper'\n\nRSpec.describe "
RSPEC_START_2 = ", type: :policy do\n  let(:user) { create(:user) }\n  let(:context) { { user: } }\n  let(:policy) { described_class.new(user:) }\n\n"
RSPEC_END = "end"
