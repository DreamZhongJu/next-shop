import 'package:flutter/material.dart';
import 'package:flutter_jdshop/pages/tabs/Tabs.dart';
import 'package:flutter_jdshop/routers/router.dart';
import 'package:flutter_jdshop/services/ScreenAdaper.dart';
import 'package:flutter_jdshop/services/AppState.dart';
import 'package:flutter_jdshop/services/StorageService.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:provider/provider.dart';
import 'package:google_fonts/google_fonts.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  final storageService = StorageService();
  await storageService.init();
  
  runApp(const MyApp());
}

class MyApp extends StatefulWidget {
  const MyApp({super.key});

  @override
  State<MyApp> createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {
  @override
  Widget build(BuildContext context) {
    return ScreenAdapter.init(
      child: MultiProvider(
        providers: [
          ChangeNotifierProvider(create: (_) => AppState()),
        ],
        child: MaterialApp(
          title: "JD Shop",
          theme: ThemeData(
            primarySwatch: Colors.blue,
            fontFamily: GoogleFonts.inter().fontFamily,
            appBarTheme: AppBarTheme(
              elevation: 0,
              backgroundColor: Colors.white,
              foregroundColor: Colors.black,
              titleTextStyle: GoogleFonts.inter(
                fontSize: 18,
                fontWeight: FontWeight.w600,
                color: Colors.black,
              ),
            ),
            textTheme: GoogleFonts.interTextTheme(),
            colorScheme: ColorScheme.fromSwatch(
              primarySwatch: Colors.blue,
              backgroundColor: Colors.white,
            ),
            inputDecorationTheme: InputDecorationTheme(
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: BorderSide(color: Colors.grey.shade300),
              ),
              enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: BorderSide(color: Colors.grey.shade300),
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: BorderSide(color: Colors.blue.shade400, width: 2),
              ),
              filled: true,
              fillColor: Colors.grey.shade50,
              contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 14),
            ),
            cardTheme: CardThemeData(
              elevation: 2,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
              ),
              margin: EdgeInsets.zero,
            ),
            buttonTheme: ButtonThemeData(
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
            elevatedButtonTheme: ElevatedButtonThemeData(
              style: ElevatedButton.styleFrom(
                foregroundColor: Colors.white,
                backgroundColor: Colors.blue.shade500,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                padding: EdgeInsets.symmetric(horizontal: 24, vertical: 14),
                textStyle: GoogleFonts.inter(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
          ),
          initialRoute: '/',
          onGenerateRoute: onGenerateRoute,
          debugShowCheckedModeBanner: false,
        ),
      ),
    );
  }
}
