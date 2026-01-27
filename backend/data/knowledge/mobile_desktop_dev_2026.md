# Мобильная и десктоп разработка 2026

## React Native 0.75+

### Основы
```tsx
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  FlatList,
  TextInput,
  Image,
  ScrollView,
  SafeAreaView,
  Platform,
} from 'react-native';

interface User {
  id: string;
  name: string;
  avatar: string;
}

const App: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await fetch('https://api.example.com/users');
      const data = await response.json();
      setUsers(data);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const filteredUsers = users.filter(user =>
    user.name.toLowerCase().includes(search.toLowerCase())
  );

  const renderItem = ({ item }: { item: User }) => (
    <TouchableOpacity style={styles.userCard}>
      <Image source={{ uri: item.avatar }} style={styles.avatar} />
      <Text style={styles.userName}>{item.name}</Text>
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={styles.container}>
      <TextInput
        style={styles.searchInput}
        placeholder="Search users..."
        value={search}
        onChangeText={setSearch}
      />
      <FlatList
        data={filteredUsers}
        renderItem={renderItem}
        keyExtractor={item => item.id}
        refreshing={loading}
        onRefresh={fetchUsers}
      />
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  searchInput: {
    margin: 16,
    padding: 12,
    borderRadius: 8,
    backgroundColor: '#f5f5f5',
  },
  userCard: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  avatar: {
    width: 50,
    height: 50,
    borderRadius: 25,
    marginRight: 12,
  },
  userName: {
    fontSize: 16,
    fontWeight: '500',
  },
});

export default App;
```

### Navigation (React Navigation 7)
```tsx
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';

type RootStackParamList = {
  Home: undefined;
  Profile: { userId: string };
  Settings: undefined;
};

const Stack = createNativeStackNavigator<RootStackParamList>();
const Tab = createBottomTabNavigator();

function HomeScreen({ navigation }) {
  return (
    <View>
      <Button
        title="Go to Profile"
        onPress={() => navigation.navigate('Profile', { userId: '123' })}
      />
    </View>
  );
}

function ProfileScreen({ route }) {
  const { userId } = route.params;
  return <Text>User ID: {userId}</Text>;
}

function TabNavigator() {
  return (
    <Tab.Navigator>
      <Tab.Screen name="Home" component={HomeScreen} />
      <Tab.Screen name="Settings" component={SettingsScreen} />
    </Tab.Navigator>
  );
}

function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator>
        <Stack.Screen name="Main" component={TabNavigator} />
        <Stack.Screen name="Profile" component={ProfileScreen} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
```

### State Management (Zustand)
```tsx
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      login: async (email, password) => {
        const response = await api.login(email, password);
        set({
          user: response.user,
          token: response.token,
          isAuthenticated: true,
        });
      },
      logout: () => {
        set({ user: null, token: null, isAuthenticated: false });
      },
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => AsyncStorage),
    }
  )
);

// Usage
function LoginScreen() {
  const { login, isAuthenticated } = useAuthStore();
  
  const handleLogin = async () => {
    await login('user@example.com', 'password');
  };
  
  return (
    <Button title="Login" onPress={handleLogin} />
  );
}
```

---

## Flutter 3.20+

### Основы
```dart
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Flutter App',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
        useMaterial3: true,
      ),
      home: const HomePage(),
    );
  }
}

class User {
  final String id;
  final String name;
  final String email;

  User({required this.id, required this.name, required this.email});

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'],
      name: json['name'],
      email: json['email'],
    );
  }
}

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  List<User> users = [];
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    fetchUsers();
  }

  Future<void> fetchUsers() async {
    try {
      final response = await http.get(
        Uri.parse('https://api.example.com/users'),
      );
      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body);
        setState(() {
          users = data.map((json) => User.fromJson(json)).toList();
          isLoading = false;
        });
      }
    } catch (e) {
      setState(() => isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Users'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
      ),
      body: isLoading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: fetchUsers,
              child: ListView.builder(
                itemCount: users.length,
                itemBuilder: (context, index) {
                  final user = users[index];
                  return ListTile(
                    leading: CircleAvatar(
                      child: Text(user.name[0]),
                    ),
                    title: Text(user.name),
                    subtitle: Text(user.email),
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => UserDetailPage(user: user),
                        ),
                      );
                    },
                  );
                },
              ),
            ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {},
        child: const Icon(Icons.add),
      ),
    );
  }
}
```

### State Management (Riverpod 2.0)
```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Provider
final counterProvider = StateProvider<int>((ref) => 0);

// Notifier
class UserNotifier extends AsyncNotifier<List<User>> {
  @override
  Future<List<User>> build() async {
    return fetchUsers();
  }

  Future<List<User>> fetchUsers() async {
    final response = await http.get(Uri.parse('https://api.example.com/users'));
    final data = json.decode(response.body) as List;
    return data.map((json) => User.fromJson(json)).toList();
  }

  Future<void> addUser(User user) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      await api.createUser(user);
      return fetchUsers();
    });
  }
}

final usersProvider = AsyncNotifierProvider<UserNotifier, List<User>>(
  () => UserNotifier(),
);

// Usage
class UsersPage extends ConsumerWidget {
  const UsersPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final usersAsync = ref.watch(usersProvider);

    return usersAsync.when(
      data: (users) => ListView.builder(
        itemCount: users.length,
        itemBuilder: (context, index) => ListTile(
          title: Text(users[index].name),
        ),
      ),
      loading: () => const CircularProgressIndicator(),
      error: (error, stack) => Text('Error: $error'),
    );
  }
}
```

---

## Swift (iOS) - SwiftUI

```swift
import SwiftUI

// Model
struct User: Identifiable, Codable {
    let id: String
    let name: String
    let email: String
}

// ViewModel
@MainActor
class UsersViewModel: ObservableObject {
    @Published var users: [User] = []
    @Published var isLoading = false
    @Published var error: Error?
    
    func fetchUsers() async {
        isLoading = true
        defer { isLoading = false }
        
        do {
            let url = URL(string: "https://api.example.com/users")!
            let (data, _) = try await URLSession.shared.data(from: url)
            users = try JSONDecoder().decode([User].self, from: data)
        } catch {
            self.error = error
        }
    }
}

// View
struct UsersView: View {
    @StateObject private var viewModel = UsersViewModel()
    @State private var searchText = ""
    
    var filteredUsers: [User] {
        if searchText.isEmpty {
            return viewModel.users
        }
        return viewModel.users.filter { $0.name.localizedCaseInsensitiveContains(searchText) }
    }
    
    var body: some View {
        NavigationStack {
            List(filteredUsers) { user in
                NavigationLink(value: user) {
                    HStack {
                        Image(systemName: "person.circle.fill")
                            .font(.largeTitle)
                            .foregroundColor(.blue)
                        
                        VStack(alignment: .leading) {
                            Text(user.name)
                                .font(.headline)
                            Text(user.email)
                                .font(.subheadline)
                                .foregroundColor(.gray)
                        }
                    }
                }
            }
            .navigationTitle("Users")
            .searchable(text: $searchText)
            .refreshable {
                await viewModel.fetchUsers()
            }
            .navigationDestination(for: User.self) { user in
                UserDetailView(user: user)
            }
            .overlay {
                if viewModel.isLoading {
                    ProgressView()
                }
            }
        }
        .task {
            await viewModel.fetchUsers()
        }
    }
}

// App
@main
struct MyApp: App {
    var body: some Scene {
        WindowGroup {
            UsersView()
        }
    }
}
```

---

## Kotlin (Android) - Jetpack Compose

```kotlin
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

// Model
data class User(
    val id: String,
    val name: String,
    val email: String
)

// ViewModel
class UsersViewModel : ViewModel() {
    private val _uiState = MutableStateFlow<UsersUiState>(UsersUiState.Loading)
    val uiState: StateFlow<UsersUiState> = _uiState

    init {
        fetchUsers()
    }

    fun fetchUsers() {
        viewModelScope.launch {
            _uiState.value = UsersUiState.Loading
            try {
                val users = api.getUsers()
                _uiState.value = UsersUiState.Success(users)
            } catch (e: Exception) {
                _uiState.value = UsersUiState.Error(e.message ?: "Unknown error")
            }
        }
    }
}

sealed class UsersUiState {
    object Loading : UsersUiState()
    data class Success(val users: List<User>) : UsersUiState()
    data class Error(val message: String) : UsersUiState()
}

// Composable
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun UsersScreen(
    viewModel: UsersViewModel = viewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    var searchQuery by remember { mutableStateOf("") }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Users") }
            )
        },
        floatingActionButton = {
            FloatingActionButton(onClick = { /* Add user */ }) {
                Icon(Icons.Default.Add, contentDescription = "Add")
            }
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            OutlinedTextField(
                value = searchQuery,
                onValueChange = { searchQuery = it },
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                placeholder = { Text("Search users...") }
            )

            when (val state = uiState) {
                is UsersUiState.Loading -> {
                    Box(
                        modifier = Modifier.fillMaxSize(),
                        contentAlignment = Alignment.Center
                    ) {
                        CircularProgressIndicator()
                    }
                }
                is UsersUiState.Success -> {
                    val filteredUsers = state.users.filter {
                        it.name.contains(searchQuery, ignoreCase = true)
                    }
                    LazyColumn {
                        items(filteredUsers) { user ->
                            UserItem(user = user)
                        }
                    }
                }
                is UsersUiState.Error -> {
                    Text(
                        text = state.message,
                        color = MaterialTheme.colorScheme.error,
                        modifier = Modifier.padding(16.dp)
                    )
                }
            }
        }
    }
}

@Composable
fun UserItem(user: User) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp)
    ) {
        Row(
            modifier = Modifier.padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                Icons.Default.Person,
                contentDescription = null,
                modifier = Modifier.size(48.dp)
            )
            Spacer(modifier = Modifier.width(16.dp))
            Column {
                Text(
                    text = user.name,
                    style = MaterialTheme.typography.titleMedium
                )
                Text(
                    text = user.email,
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}
```

---

## Electron (Desktop)

```typescript
// main.ts
import { app, BrowserWindow, ipcMain, dialog } from 'electron';
import path from 'path';

let mainWindow: BrowserWindow | null = null;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  if (process.env.NODE_ENV === 'development') {
    mainWindow.loadURL('http://localhost:5173');
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
  }
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// IPC handlers
ipcMain.handle('open-file', async () => {
  const result = await dialog.showOpenDialog(mainWindow!, {
    properties: ['openFile'],
    filters: [{ name: 'All Files', extensions: ['*'] }],
  });
  return result.filePaths[0];
});

ipcMain.handle('save-file', async (_, content: string) => {
  const result = await dialog.showSaveDialog(mainWindow!, {
    filters: [{ name: 'Text Files', extensions: ['txt'] }],
  });
  if (!result.canceled && result.filePath) {
    await fs.writeFile(result.filePath, content);
    return result.filePath;
  }
  return null;
});

// preload.ts
import { contextBridge, ipcRenderer } from 'electron';

contextBridge.exposeInMainWorld('electronAPI', {
  openFile: () => ipcRenderer.invoke('open-file'),
  saveFile: (content: string) => ipcRenderer.invoke('save-file', content),
  onMenuAction: (callback: (action: string) => void) => {
    ipcRenderer.on('menu-action', (_, action) => callback(action));
  },
});

// renderer (React)
declare global {
  interface Window {
    electronAPI: {
      openFile: () => Promise<string>;
      saveFile: (content: string) => Promise<string | null>;
      onMenuAction: (callback: (action: string) => void) => void;
    };
  }
}

function App() {
  const handleOpen = async () => {
    const filePath = await window.electronAPI.openFile();
    console.log('Selected file:', filePath);
  };

  return (
    <button onClick={handleOpen}>Open File</button>
  );
}
```

---

## Tauri 2.0 (Rust + Web)

```rust
// src-tauri/src/main.rs
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri::{Manager, State};
use std::sync::Mutex;

struct AppState {
    counter: Mutex<i32>,
}

#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}!", name)
}

#[tauri::command]
fn increment(state: State<AppState>) -> i32 {
    let mut counter = state.counter.lock().unwrap();
    *counter += 1;
    *counter
}

#[tauri::command]
async fn fetch_data(url: String) -> Result<String, String> {
    reqwest::get(&url)
        .await
        .map_err(|e| e.to_string())?
        .text()
        .await
        .map_err(|e| e.to_string())
}

fn main() {
    tauri::Builder::default()
        .manage(AppState {
            counter: Mutex::new(0),
        })
        .invoke_handler(tauri::generate_handler![greet, increment, fetch_data])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

```typescript
// Frontend (React/Vue/Svelte)
import { invoke } from '@tauri-apps/api/tauri';
import { open, save } from '@tauri-apps/api/dialog';
import { readTextFile, writeTextFile } from '@tauri-apps/api/fs';

async function greetUser(name: string) {
  const greeting = await invoke<string>('greet', { name });
  console.log(greeting);
}

async function openFile() {
  const selected = await open({
    multiple: false,
    filters: [{ name: 'Text', extensions: ['txt', 'md'] }],
  });
  
  if (selected && typeof selected === 'string') {
    const content = await readTextFile(selected);
    return content;
  }
}

async function saveFile(content: string) {
  const filePath = await save({
    filters: [{ name: 'Text', extensions: ['txt'] }],
  });
  
  if (filePath) {
    await writeTextFile(filePath, content);
  }
}
```

---

## .NET MAUI (Cross-platform)

```csharp
// MainPage.xaml.cs
using Microsoft.Maui.Controls;

public partial class MainPage : ContentPage
{
    private readonly IUserService _userService;

    public MainPage(IUserService userService)
    {
        InitializeComponent();
        _userService = userService;
        BindingContext = new MainViewModel(userService);
    }
}

// MainViewModel.cs
public partial class MainViewModel : ObservableObject
{
    private readonly IUserService _userService;

    [ObservableProperty]
    private ObservableCollection<User> users = new();

    [ObservableProperty]
    private bool isLoading;

    [ObservableProperty]
    private string searchQuery = string.Empty;

    public MainViewModel(IUserService userService)
    {
        _userService = userService;
        LoadUsersCommand.Execute(null);
    }

    [RelayCommand]
    private async Task LoadUsers()
    {
        IsLoading = true;
        try
        {
            var result = await _userService.GetUsersAsync();
            Users = new ObservableCollection<User>(result);
        }
        finally
        {
            IsLoading = false;
        }
    }

    partial void OnSearchQueryChanged(string value)
    {
        // Filter users
    }
}

// MainPage.xaml
<?xml version="1.0" encoding="utf-8" ?>
<ContentPage xmlns="http://schemas.microsoft.com/dotnet/2021/maui"
             xmlns:x="http://schemas.microsoft.com/winfx/2009/xaml"
             x:Class="MyApp.MainPage">
    <Grid RowDefinitions="Auto,*">
        <SearchBar Text="{Binding SearchQuery}"
                   Placeholder="Search users..." />
        
        <CollectionView Grid.Row="1"
                        ItemsSource="{Binding Users}">
            <CollectionView.ItemTemplate>
                <DataTemplate>
                    <Frame Margin="10" Padding="10">
                        <StackLayout>
                            <Label Text="{Binding Name}"
                                   FontSize="18"
                                   FontAttributes="Bold" />
                            <Label Text="{Binding Email}"
                                   TextColor="Gray" />
                        </StackLayout>
                    </Frame>
                </DataTemplate>
            </CollectionView.ItemTemplate>
        </CollectionView>
        
        <ActivityIndicator Grid.RowSpan="2"
                           IsRunning="{Binding IsLoading}"
                           IsVisible="{Binding IsLoading}" />
    </Grid>
</ContentPage>
```

---

## Qt 6 (C++ Desktop)

```cpp
// mainwindow.h
#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QListWidget>
#include <QLineEdit>
#include <QPushButton>
#include <QNetworkAccessManager>

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    MainWindow(QWidget *parent = nullptr);
    ~MainWindow();

private slots:
    void onFetchUsers();
    void onNetworkReply(QNetworkReply *reply);
    void onSearchChanged(const QString &text);

private:
    QListWidget *userList;
    QLineEdit *searchInput;
    QPushButton *refreshButton;
    QNetworkAccessManager *networkManager;
    QVector<QPair<QString, QString>> users;
    
    void setupUI();
    void filterUsers(const QString &query);
};

#endif

// mainwindow.cpp
#include "mainwindow.h"
#include <QVBoxLayout>
#include <QNetworkReply>
#include <QJsonDocument>
#include <QJsonArray>
#include <QJsonObject>

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
{
    setupUI();
    networkManager = new QNetworkAccessManager(this);
    connect(networkManager, &QNetworkAccessManager::finished,
            this, &MainWindow::onNetworkReply);
    onFetchUsers();
}

void MainWindow::setupUI()
{
    QWidget *central = new QWidget(this);
    QVBoxLayout *layout = new QVBoxLayout(central);
    
    searchInput = new QLineEdit(this);
    searchInput->setPlaceholderText("Search users...");
    connect(searchInput, &QLineEdit::textChanged,
            this, &MainWindow::onSearchChanged);
    
    userList = new QListWidget(this);
    
    refreshButton = new QPushButton("Refresh", this);
    connect(refreshButton, &QPushButton::clicked,
            this, &MainWindow::onFetchUsers);
    
    layout->addWidget(searchInput);
    layout->addWidget(userList);
    layout->addWidget(refreshButton);
    
    setCentralWidget(central);
    setWindowTitle("Users");
    resize(400, 600);
}

void MainWindow::onFetchUsers()
{
    QNetworkRequest request(QUrl("https://api.example.com/users"));
    networkManager->get(request);
}

void MainWindow::onNetworkReply(QNetworkReply *reply)
{
    if (reply->error() == QNetworkReply::NoError) {
        QJsonDocument doc = QJsonDocument::fromJson(reply->readAll());
        QJsonArray array = doc.array();
        
        users.clear();
        for (const QJsonValue &value : array) {
            QJsonObject obj = value.toObject();
            users.append({obj["name"].toString(), obj["email"].toString()});
        }
        filterUsers(searchInput->text());
    }
    reply->deleteLater();
}

void MainWindow::filterUsers(const QString &query)
{
    userList->clear();
    for (const auto &user : users) {
        if (user.first.contains(query, Qt::CaseInsensitive)) {
            userList->addItem(QString("%1 (%2)").arg(user.first, user.second));
        }
    }
}
```

Источники: Официальная документация платформ, 2024-2026
